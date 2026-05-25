/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
/*                                                                       */
/*    This file is part of the HiGHS linear optimization suite           */
/*                                                                       */
/*    Available as open-source under the MIT License                     */
/*                                                                       */
/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
#ifndef QUANTUM_HIGHS_QUANTUM_OPTIONS_H_
#define QUANTUM_HIGHS_QUANTUM_OPTIONS_H_

#ifdef QUANTUM

#include <string>

namespace highs_quantum {

// Subprocess protocol version. Bumped if the JSON schema in
// highspy_quantum/protocol.py changes incompatibly.
constexpr int kProtocolVersion = 1;

// Default Python module to invoke. The runtime command becomes:
//   ${quantum_python_executable} -m ${kPythonModule} solve ...
constexpr const char* kPythonModule = "highspy_quantum";

// Environment variable that, when set, overrides the temp-file directory used
// for the JSON protocol files. Defaults to /tmp.
constexpr const char* kTmpDirEnv = "HIGHS_QUANTUM_TMPDIR";

}  // namespace highs_quantum

#endif  // QUANTUM
#endif  // QUANTUM_HIGHS_QUANTUM_OPTIONS_H_
