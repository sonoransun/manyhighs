//! The GIL-free parallel runtime: solve many independent models across OS
//! threads, each owning its own [`Highs`] instance.
//!
//! HiGHS's work-stealing scheduler lives in thread-local storage, and a `Highs`
//! instance is [`Send`], so N instances can solve concurrently on N threads with
//! no shared mutable state — the thing Python's GIL prevents. To avoid CPU
//! oversubscription, give each instance `threads = 1` (the default of every API
//! here); see [`recommended_inner_threads`].

use crate::callback::CallbackAction;
use crate::enums::{CallbackType, ModelStatus};
use crate::error::Result;
use crate::model::Highs;
use crate::solution::Solution;
use highs_sys::{self as sys, HighsInt};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;

/// Number of logical CPUs, or 1 if undetectable.
pub fn available_parallelism() -> usize {
    thread::available_parallelism().map(|n| n.get()).unwrap_or(1)
}

/// Internal threads per instance when running `pool_threads` solves at once on
/// this machine. Floors at 1 so a pool never oversubscribes the CPUs.
pub fn recommended_inner_threads(pool_threads: usize) -> usize {
    (available_parallelism() / pool_threads.max(1)).max(1)
}

/// The result of one solve in a batch.
#[derive(Debug, Clone, PartialEq)]
pub struct SolveOutcome {
    pub status: ModelStatus,
    pub objective: f64,
    pub solution: Solution,
}

/// Knobs for [`solve_many`].
#[derive(Debug, Clone, Copy)]
pub struct SolveOptions {
    /// Internal HiGHS threads per instance (default 1).
    pub inner_threads: usize,
    /// Number of OS worker threads (default = logical CPUs).
    pub pool_threads: usize,
}

impl Default for SolveOptions {
    fn default() -> Self {
        SolveOptions {
            inner_threads: 1,
            pool_threads: available_parallelism(),
        }
    }
}

fn configure(h: &mut Highs, inner_threads: usize) {
    let _ = h.set_output(false);
    let _ = h.set_threads(inner_threads.max(1) as i32);
}

fn solve_outcome(h: &mut Highs) -> Result<SolveOutcome> {
    let status = h.run()?;
    Ok(SolveOutcome {
        status,
        objective: h.objective_value(),
        solution: h.solution()?,
    })
}

/// Build and solve many independent models in parallel, preserving input order.
///
/// Each OS worker owns one [`Highs`] instance reused across its share of the
/// work via [`Highs::clear_model`], so model build, solve, and extraction never
/// touch shared state. Builders may borrow from the caller's stack (they run
/// inside a [`std::thread::scope`]).
///
/// ```
/// use highs::parallel::{solve_many, SolveOptions};
/// let builders: Vec<_> = (1..=8).map(|k| move |h: &mut highs::Highs| {
///     let x = h.add_var(0.0, 1.0e30)?;
///     h.add_constr(x.ge(k as f64))?;
///     h.minimize(x)
/// }).collect();
/// let results = solve_many(builders, SolveOptions::default());
/// for (i, r) in results.iter().enumerate() {
///     assert!((r.as_ref().unwrap().objective - (i as f64 + 1.0)).abs() < 1e-9);
/// }
/// ```
pub fn solve_many<F>(builders: Vec<F>, opts: SolveOptions) -> Vec<Result<SolveOutcome>>
where
    F: FnOnce(&mut Highs) -> Result<()> + Send,
{
    let n = builders.len();
    if n == 0 {
        return Vec::new();
    }
    let pool = opts.pool_threads.max(1).min(n);
    let inner = opts.inner_threads;

    let queue = Mutex::new(builders.into_iter().enumerate());
    let results: Vec<Mutex<Option<Result<SolveOutcome>>>> =
        (0..n).map(|_| Mutex::new(None)).collect();

    thread::scope(|scope| {
        for _ in 0..pool {
            scope.spawn(|| {
                let mut h = Highs::new();
                configure(&mut h, inner);
                loop {
                    let next = queue.lock().unwrap().next();
                    let (idx, build) = match next {
                        Some(item) => item,
                        None => break,
                    };
                    let outcome = (|| {
                        h.clear_model()?;
                        build(&mut h)?;
                        solve_outcome(&mut h)
                    })();
                    *results[idx].lock().unwrap() = Some(outcome);
                }
            });
        }
    });

    results
        .into_iter()
        .map(|m| m.into_inner().unwrap().expect("every slot filled"))
        .collect()
}

/// Solve many models in parallel with rayon's thread pool. Each task constructs
/// its own instance (pinned to one internal thread), so the produced
/// [`SolveOutcome`]s never share state.
#[cfg(feature = "rayon")]
pub fn par_solve_many<S, F>(specs: &[S], build: F) -> Vec<Result<SolveOutcome>>
where
    S: Sync,
    F: Fn(&S, &mut Highs) -> Result<()> + Sync,
{
    use rayon::prelude::*;
    specs
        .par_iter()
        .map(|spec| {
            let mut h = Highs::new();
            configure(&mut h, 1);
            build(spec, &mut h)?;
            solve_outcome(&mut h)
        })
        .collect()
}

/// A pool of reusable [`Highs`] instances for streaming workloads, avoiding
/// repeated create/destroy and scheduler initialization. Cheaply shareable via
/// `Arc<HighsPool>` across threads.
pub struct HighsPool {
    idle: Mutex<Vec<Highs>>,
    inner_threads: usize,
}

impl HighsPool {
    /// Pre-create `size` instances, each pinned to `inner_threads` internal threads.
    pub fn new(size: usize, inner_threads: usize) -> Self {
        let mut idle = Vec::with_capacity(size);
        for _ in 0..size {
            let mut h = Highs::new();
            configure(&mut h, inner_threads);
            idle.push(h);
        }
        HighsPool {
            idle: Mutex::new(idle),
            inner_threads,
        }
    }

    /// Check out an instance (its model already cleared), run `f`, and return it.
    pub fn with<R>(&self, f: impl FnOnce(&mut Highs) -> R) -> R {
        let mut h = self.checkout();
        let r = f(&mut h);
        self.checkin(h);
        r
    }

    fn checkout(&self) -> Highs {
        if let Some(h) = self.idle.lock().unwrap().pop() {
            h
        } else {
            let mut h = Highs::new();
            configure(&mut h, self.inner_threads);
            h
        }
    }

    fn checkin(&self, mut h: Highs) {
        let _ = h.clear_model();
        self.idle.lock().unwrap().push(h);
    }
}

/// A cooperative cancellation flag shared across threads. Wire it into an
/// instance with [`Highs::set_cancel_token`], then `cancel()` from any thread.
#[derive(Clone, Default)]
pub struct CancelToken(Arc<AtomicBool>);

impl CancelToken {
    pub fn new() -> Self {
        Self::default()
    }

    /// Request cancellation of any solve watching this token.
    pub fn cancel(&self) {
        self.0.store(true, Ordering::Relaxed);
    }

    /// Whether cancellation has been requested.
    pub fn is_cancelled(&self) -> bool {
        self.0.load(Ordering::Relaxed)
    }
}

/// A solve running on its own OS thread, cancellable from elsewhere.
pub struct RunningSolve {
    handle: thread::JoinHandle<Result<(ModelStatus, Highs)>>,
    token: CancelToken,
}

impl RunningSolve {
    /// Request cancellation; the solve stops at its next interrupt check.
    pub fn cancel(&self) {
        self.token.cancel();
    }

    /// A clone of the cancellation token.
    pub fn token(&self) -> CancelToken {
        self.token.clone()
    }

    /// Wait for the solve to finish, recovering the status and the instance
    /// (from which the solution can be extracted).
    pub fn join(self) -> Result<(ModelStatus, Highs)> {
        self.handle.join().expect("solve thread panicked")
    }
}

impl Highs {
    /// Install a cancellation token: a callback checks it and interrupts the
    /// solve when cancelled. Enables the simplex/IPM/MIP interrupt categories.
    /// Replaces any previously set callback.
    pub fn set_cancel_token(&mut self, token: CancelToken) -> Result<()> {
        self.set_callback(move |_ctx| {
            if token.is_cancelled() {
                CallbackAction::Interrupt
            } else {
                CallbackAction::Continue
            }
        })?;
        self.start_callback(CallbackType::SimplexInterrupt)?;
        self.start_callback(CallbackType::IpmInterrupt)?;
        self.start_callback(CallbackType::MipInterrupt)?;
        Ok(())
    }

    /// Move this instance onto a new OS thread and run it, returning a handle
    /// that can be cancelled from any thread and joined for the result.
    pub fn start_solve(mut self) -> RunningSolve {
        let token = CancelToken::new();
        let _ = self.set_cancel_token(token.clone());
        let handle = thread::spawn(move || {
            let status = self.run()?;
            Ok((status, self))
        });
        RunningSolve { handle, token }
    }

    /// Tear down the calling thread's HiGHS worker scheduler.
    ///
    /// Rarely needed: with the recommended `threads = 1` many-instance pattern
    /// there are no extra worker threads to tear down. It matters only after
    /// internal-parallel (`threads > 1`) solves on a thread that is exiting or
    /// must change its thread count.
    ///
    /// # Safety contract
    /// Must not be called while any `Highs` instance is running on *any* thread
    /// (per the C API). `blocking` only joins workers when called on the main
    /// thread; on a spawned thread it detaches them to avoid a join deadlock.
    pub fn reset_scheduler(blocking: bool) {
        unsafe { sys::Highs_resetGlobalScheduler(blocking as HighsInt) };
    }
}

/// RAII guard that resets the calling thread's scheduler (non-blocking) on drop.
/// Place at the end of a worker closure that ran internal-parallel solves.
#[derive(Debug, Default)]
pub struct SchedulerResetOnDrop;

impl Drop for SchedulerResetOnDrop {
    fn drop(&mut self) {
        Highs::reset_scheduler(false);
    }
}
