/* Single entry point for bindgen. The C API header pulls in
 * lp_data/HighsCallbackStruct.h -> util/HighsInt.h -> HConfig.h, all of which
 * are reachable with -I<repo>/highs and -I<dir containing HConfig.h>. */
#include "interfaces/highs_c_api.h"
