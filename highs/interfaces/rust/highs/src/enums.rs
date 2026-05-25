//! Strongly-typed mirrors of the `kHighs*` C constants.
//!
//! Each enum's `as_raw`/`from_raw` is defined in terms of the `highs_sys`
//! constants, so the mapping can never drift from the compiled library.

use highs_sys as sys;

/// Optimization direction.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ObjSense {
    Minimize,
    Maximize,
}

impl ObjSense {
    pub(crate) fn as_raw(self) -> sys::HighsInt {
        match self {
            ObjSense::Minimize => sys::kHighsObjSenseMinimize,
            ObjSense::Maximize => sys::kHighsObjSenseMaximize,
        }
    }

    pub(crate) fn from_raw(c: sys::HighsInt) -> Self {
        if c == sys::kHighsObjSenseMaximize {
            ObjSense::Maximize
        } else {
            ObjSense::Minimize
        }
    }
}

/// Variable type / integrality.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum VarType {
    Continuous,
    Integer,
    SemiContinuous,
    SemiInteger,
    ImplicitInteger,
}

impl VarType {
    pub(crate) fn as_raw(self) -> sys::HighsInt {
        match self {
            VarType::Continuous => sys::kHighsVarTypeContinuous,
            VarType::Integer => sys::kHighsVarTypeInteger,
            VarType::SemiContinuous => sys::kHighsVarTypeSemiContinuous,
            VarType::SemiInteger => sys::kHighsVarTypeSemiInteger,
            VarType::ImplicitInteger => sys::kHighsVarTypeImplicitInteger,
        }
    }

    pub(crate) fn from_raw(c: sys::HighsInt) -> Self {
        match c {
            x if x == sys::kHighsVarTypeInteger => VarType::Integer,
            x if x == sys::kHighsVarTypeSemiContinuous => VarType::SemiContinuous,
            x if x == sys::kHighsVarTypeSemiInteger => VarType::SemiInteger,
            x if x == sys::kHighsVarTypeImplicitInteger => VarType::ImplicitInteger,
            _ => VarType::Continuous,
        }
    }
}

/// Sparse matrix orientation.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum MatrixFormat {
    /// Compressed sparse column.
    #[default]
    ColWise,
    /// Compressed sparse row.
    RowWise,
}

impl MatrixFormat {
    pub(crate) fn as_raw(self) -> sys::HighsInt {
        match self {
            MatrixFormat::ColWise => sys::kHighsMatrixFormatColwise,
            MatrixFormat::RowWise => sys::kHighsMatrixFormatRowwise,
        }
    }
}

/// Hessian storage format for QP.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HessianFormat {
    Triangular,
    Square,
}

impl HessianFormat {
    pub(crate) fn as_raw(self) -> sys::HighsInt {
        match self {
            HessianFormat::Triangular => sys::kHighsHessianFormatTriangular,
            HessianFormat::Square => sys::kHighsHessianFormatSquare,
        }
    }
}

/// Runtime type of an option.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum OptionType {
    Bool,
    Int,
    Double,
    String,
}

impl OptionType {
    pub(crate) fn from_raw(c: sys::HighsInt) -> Self {
        match c {
            x if x == sys::kHighsOptionTypeInt => OptionType::Int,
            x if x == sys::kHighsOptionTypeDouble => OptionType::Double,
            x if x == sys::kHighsOptionTypeString => OptionType::String,
            _ => OptionType::Bool,
        }
    }
}

/// Per-variable / per-constraint basis status.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BasisStatus {
    Lower,
    Basic,
    Upper,
    Zero,
    Nonbasic,
}

impl BasisStatus {
    pub(crate) fn from_raw(c: sys::HighsInt) -> Self {
        match c {
            x if x == sys::kHighsBasisStatusBasic => BasisStatus::Basic,
            x if x == sys::kHighsBasisStatusUpper => BasisStatus::Upper,
            x if x == sys::kHighsBasisStatusZero => BasisStatus::Zero,
            x if x == sys::kHighsBasisStatusNonbasic => BasisStatus::Nonbasic,
            _ => BasisStatus::Lower,
        }
    }
}

/// Outcome of a solve, mirroring `kHighsModelStatus*`.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ModelStatus {
    NotSet,
    LoadError,
    ModelError,
    PresolveError,
    SolveError,
    PostsolveError,
    ModelEmpty,
    Optimal,
    Infeasible,
    UnboundedOrInfeasible,
    Unbounded,
    ObjectiveBound,
    ObjectiveTarget,
    TimeLimit,
    IterationLimit,
    SolutionLimit,
    Interrupt,
    Unknown,
}

impl ModelStatus {
    pub(crate) fn from_raw(c: sys::HighsInt) -> Self {
        match c {
            x if x == sys::kHighsModelStatusLoadError => ModelStatus::LoadError,
            x if x == sys::kHighsModelStatusModelError => ModelStatus::ModelError,
            x if x == sys::kHighsModelStatusPresolveError => ModelStatus::PresolveError,
            x if x == sys::kHighsModelStatusSolveError => ModelStatus::SolveError,
            x if x == sys::kHighsModelStatusPostsolveError => ModelStatus::PostsolveError,
            x if x == sys::kHighsModelStatusModelEmpty => ModelStatus::ModelEmpty,
            x if x == sys::kHighsModelStatusOptimal => ModelStatus::Optimal,
            x if x == sys::kHighsModelStatusInfeasible => ModelStatus::Infeasible,
            x if x == sys::kHighsModelStatusUnboundedOrInfeasible => {
                ModelStatus::UnboundedOrInfeasible
            }
            x if x == sys::kHighsModelStatusUnbounded => ModelStatus::Unbounded,
            x if x == sys::kHighsModelStatusObjectiveBound => ModelStatus::ObjectiveBound,
            x if x == sys::kHighsModelStatusObjectiveTarget => ModelStatus::ObjectiveTarget,
            x if x == sys::kHighsModelStatusTimeLimit => ModelStatus::TimeLimit,
            x if x == sys::kHighsModelStatusIterationLimit => ModelStatus::IterationLimit,
            x if x == sys::kHighsModelStatusSolutionLimit => ModelStatus::SolutionLimit,
            x if x == sys::kHighsModelStatusInterrupt => ModelStatus::Interrupt,
            x if x == sys::kHighsModelStatusUnknown => ModelStatus::Unknown,
            _ => ModelStatus::NotSet,
        }
    }

    /// Whether the solve reached a provably optimal solution.
    pub fn is_optimal(self) -> bool {
        matches!(self, ModelStatus::Optimal)
    }
}

/// Callback categories, mirroring `kHighsCallback*`.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CallbackType {
    Logging,
    SimplexInterrupt,
    IpmInterrupt,
    MipSolution,
    MipImprovingSolution,
    MipLogging,
    MipInterrupt,
    MipGetCutPool,
    MipDefineLazyConstraints,
    MipUserSolution,
}

impl CallbackType {
    pub(crate) fn as_raw(self) -> sys::HighsInt {
        match self {
            CallbackType::Logging => sys::kHighsCallbackLogging,
            CallbackType::SimplexInterrupt => sys::kHighsCallbackSimplexInterrupt,
            CallbackType::IpmInterrupt => sys::kHighsCallbackIpmInterrupt,
            CallbackType::MipSolution => sys::kHighsCallbackMipSolution,
            CallbackType::MipImprovingSolution => sys::kHighsCallbackMipImprovingSolution,
            CallbackType::MipLogging => sys::kHighsCallbackMipLogging,
            CallbackType::MipInterrupt => sys::kHighsCallbackMipInterrupt,
            CallbackType::MipGetCutPool => sys::kHighsCallbackMipGetCutPool,
            CallbackType::MipDefineLazyConstraints => sys::kHighsCallbackMipDefineLazyConstraints,
            // Note: the C header constant carries a historical `Callback` typo.
            CallbackType::MipUserSolution => sys::kHighsCallbackCallbackMipUserSolution,
        }
    }

    /// Whether setting `user_interrupt` is honored for this callback type.
    /// HiGHS forbids (and in debug builds asserts against) interrupting from the
    /// MIP information callbacks.
    pub(crate) fn allows_interrupt(self) -> bool {
        !matches!(
            self,
            CallbackType::MipImprovingSolution
                | CallbackType::MipSolution
                | CallbackType::MipLogging
                | CallbackType::MipGetCutPool
                | CallbackType::MipDefineLazyConstraints
                | CallbackType::MipUserSolution
        )
    }

    pub(crate) fn from_raw(c: sys::HighsInt) -> Self {
        match c {
            x if x == sys::kHighsCallbackSimplexInterrupt => CallbackType::SimplexInterrupt,
            x if x == sys::kHighsCallbackIpmInterrupt => CallbackType::IpmInterrupt,
            x if x == sys::kHighsCallbackMipSolution => CallbackType::MipSolution,
            x if x == sys::kHighsCallbackMipImprovingSolution => CallbackType::MipImprovingSolution,
            x if x == sys::kHighsCallbackMipLogging => CallbackType::MipLogging,
            x if x == sys::kHighsCallbackMipInterrupt => CallbackType::MipInterrupt,
            x if x == sys::kHighsCallbackMipGetCutPool => CallbackType::MipGetCutPool,
            x if x == sys::kHighsCallbackMipDefineLazyConstraints => {
                CallbackType::MipDefineLazyConstraints
            }
            x if x == sys::kHighsCallbackCallbackMipUserSolution => CallbackType::MipUserSolution,
            _ => CallbackType::Logging,
        }
    }
}
