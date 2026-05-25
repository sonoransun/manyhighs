# Install script for directory: /root/cdev/manyhighs/highs

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdqsort" TYPE FILE FILES "/root/cdev/manyhighs/highs/../extern/pdqsort/pdqsort.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/zstr" TYPE FILE FILES "/root/cdev/manyhighs/highs/../extern/zstr/strict_fstream.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/zstr" TYPE FILE FILES "/root/cdev/manyhighs/highs/../extern/zstr/zstr.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/interfaces" TYPE FILE FILES "/root/cdev/manyhighs/highs/interfaces/highs_c_api.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/io" TYPE FILE FILES "/root/cdev/manyhighs/highs/io/Filereader.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/io" TYPE FILE FILES "/root/cdev/manyhighs/highs/io/FilereaderLp.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/io" TYPE FILE FILES "/root/cdev/manyhighs/highs/io/FilereaderMps.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/io" TYPE FILE FILES "/root/cdev/manyhighs/highs/io/HighsIO.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/io" TYPE FILE FILES "/root/cdev/manyhighs/highs/io/HMpsFF.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/io" TYPE FILE FILES "/root/cdev/manyhighs/highs/io/HMPSIO.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/io" TYPE FILE FILES "/root/cdev/manyhighs/highs/io/LoadOptions.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/io/filereaderlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/io/filereaderlp/builder.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/io/filereaderlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/io/filereaderlp/def.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/io/filereaderlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/io/filereaderlp/model.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/io/filereaderlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/io/filereaderlp/reader.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/IpxSolution.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/IpxWrapper.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HConst.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HighsAnalysis.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HighsCallback.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HighsCallbackStruct.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HighsDebug.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HighsIis.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HighsInfo.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HighsInfoDebug.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HighsLp.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HighsLpSolverObject.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HighsLpUtils.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HighsModelUtils.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HighsOptions.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HighsRanging.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HighsSolution.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HighsSolutionDebug.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HighsSolve.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HighsStatus.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/lp_data" TYPE FILE FILES "/root/cdev/manyhighs/highs/lp_data/HStruct.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/feasibilityjump.hh")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsCliqueTable.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsConflictPool.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsCutGeneration.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsCutPool.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsDebugSol.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsDomain.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsDomainChange.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsDynamicRowMatrix.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsGFkSolve.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsImplications.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsLpAggregator.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsLpRelaxation.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsMipAnalysis.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsMipSolver.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsMipSolverData.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsModkSeparator.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsNodeQueue.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsObjectiveFunction.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsPathSeparator.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsPrimalHeuristics.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsPseudocost.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsRedcostFixing.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsSearch.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsSeparation.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsSeparator.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsTableauSeparator.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/HighsTransformedLp.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/mip" TYPE FILE FILES "/root/cdev/manyhighs/highs/mip/MipTimer.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/model" TYPE FILE FILES "/root/cdev/manyhighs/highs/model/HighsHessian.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/model" TYPE FILE FILES "/root/cdev/manyhighs/highs/model/HighsHessianUtils.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/model" TYPE FILE FILES "/root/cdev/manyhighs/highs/model/HighsModel.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/parallel" TYPE FILE FILES "/root/cdev/manyhighs/highs/parallel/HighsBinarySemaphore.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/parallel" TYPE FILE FILES "/root/cdev/manyhighs/highs/parallel/HighsCacheAlign.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/parallel" TYPE FILE FILES "/root/cdev/manyhighs/highs/parallel/HighsCombinable.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/parallel" TYPE FILE FILES "/root/cdev/manyhighs/highs/parallel/HighsMutex.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/parallel" TYPE FILE FILES "/root/cdev/manyhighs/highs/parallel/HighsParallel.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/parallel" TYPE FILE FILES "/root/cdev/manyhighs/highs/parallel/HighsRaceTimer.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/parallel" TYPE FILE FILES "/root/cdev/manyhighs/highs/parallel/HighsSchedulerConstants.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/parallel" TYPE FILE FILES "/root/cdev/manyhighs/highs/parallel/HighsSpinMutex.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/parallel" TYPE FILE FILES "/root/cdev/manyhighs/highs/parallel/HighsSplitDeque.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/parallel" TYPE FILE FILES "/root/cdev/manyhighs/highs/parallel/HighsTask.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/parallel" TYPE FILE FILES "/root/cdev/manyhighs/highs/parallel/HighsTaskExecutor.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/CupdlpWrapper.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/HiPdlpTimer.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/HiPdlpWrapper.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp/hipdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/hipdlp/defs.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp/hipdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/hipdlp/linalg.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp/hipdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/hipdlp/logger.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp/hipdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/hipdlp/pdhg.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp/hipdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/hipdlp/restart.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp/hipdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/hipdlp/scaling.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp/hipdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/hipdlp/solver_results.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/presolve" TYPE FILE FILES "/root/cdev/manyhighs/highs/presolve/HighsPostsolveStack.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/presolve" TYPE FILE FILES "/root/cdev/manyhighs/highs/presolve/HighsSymmetry.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/presolve" TYPE FILE FILES "/root/cdev/manyhighs/highs/presolve/HPresolve.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/presolve" TYPE FILE FILES "/root/cdev/manyhighs/highs/presolve/HPresolveAnalysis.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/presolve" TYPE FILE FILES "/root/cdev/manyhighs/highs/presolve/ICrash.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/presolve" TYPE FILE FILES "/root/cdev/manyhighs/highs/presolve/ICrashUtil.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/presolve" TYPE FILE FILES "/root/cdev/manyhighs/highs/presolve/ICrashX.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/presolve" TYPE FILE FILES "/root/cdev/manyhighs/highs/presolve/PresolveComponent.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/a_asm.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/a_quass.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/basis.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/crashsolution.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/dantzigpricing.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/devexpricing.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/eventhandler.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/factor.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/feasibility_bounded.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/feasibility_highs.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/gradient.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/instance.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/matrix.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/perturbation.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/pricing.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/qpconst.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/qpvector.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/quass.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/ratiotest.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/runtime.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/scaling.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/settings.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/snippets.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/statistics.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/qpsolver" TYPE FILE FILES "/root/cdev/manyhighs/highs/qpsolver/steepestedgepricing.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/simplex" TYPE FILE FILES "/root/cdev/manyhighs/highs/simplex/HApp.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/simplex" TYPE FILE FILES "/root/cdev/manyhighs/highs/simplex/HEkk.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/simplex" TYPE FILE FILES "/root/cdev/manyhighs/highs/simplex/HEkkDual.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/simplex" TYPE FILE FILES "/root/cdev/manyhighs/highs/simplex/HEkkDualRHS.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/simplex" TYPE FILE FILES "/root/cdev/manyhighs/highs/simplex/HEkkDualRow.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/simplex" TYPE FILE FILES "/root/cdev/manyhighs/highs/simplex/HEkkPrimal.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/simplex" TYPE FILE FILES "/root/cdev/manyhighs/highs/simplex/HighsSimplexAnalysis.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/simplex" TYPE FILE FILES "/root/cdev/manyhighs/highs/simplex/HSimplex.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/simplex" TYPE FILE FILES "/root/cdev/manyhighs/highs/simplex/HSimplexDebug.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/simplex" TYPE FILE FILES "/root/cdev/manyhighs/highs/simplex/HSimplexNla.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/simplex" TYPE FILE FILES "/root/cdev/manyhighs/highs/simplex/HSimplexReport.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/simplex" TYPE FILE FILES "/root/cdev/manyhighs/highs/simplex/SimplexConst.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/simplex" TYPE FILE FILES "/root/cdev/manyhighs/highs/simplex/SimplexStruct.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/simplex" TYPE FILE FILES "/root/cdev/manyhighs/highs/simplex/SimplexTimer.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/test_kkt" TYPE FILE FILES "/root/cdev/manyhighs/highs/test_kkt/DevKkt.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/test_kkt" TYPE FILE FILES "/root/cdev/manyhighs/highs/test_kkt/KktCh2.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/FactorTimer.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HFactor.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HFactorConst.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HFactorDebug.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsCDouble.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsComponent.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsDataStack.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsDisjointSets.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsHash.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsHashTree.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsInt.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsIntegers.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsLinearSumBounds.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsMatrixPic.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsMatrixSlice.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsMatrixUtils.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsMemoryAllocation.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsRandom.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsRbTree.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsSort.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsSparseMatrix.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsSparseVectorSum.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsSplay.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsTimer.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HighsUtils.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HSet.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HVector.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/HVectorBase.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/util" TYPE FILE FILES "/root/cdev/manyhighs/highs/util/stringutil.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs" TYPE FILE FILES "/root/cdev/manyhighs/highs/Highs.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp/cupdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/cupdlp/cupdlp_cs.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp/cupdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/cupdlp/cupdlp_defs.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp/cupdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/cupdlp/cupdlp_linalg.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp/cupdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/cupdlp/cupdlp_proj.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp/cupdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/cupdlp/cupdlp_restart.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp/cupdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/cupdlp/cupdlp_scaling.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp/cupdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/cupdlp/cupdlp_solver.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp/cupdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/cupdlp/cupdlp_step.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/pdlp/cupdlp" TYPE FILE FILES "/root/cdev/manyhighs/highs/pdlp/cupdlp/cupdlp_utils.c")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/basiclu_kernel.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/basiclu_wrapper.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/basis.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/conjugate_residuals.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/control.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/crossover.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/diagonal_precond.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/forrest_tomlin.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/guess_basis.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/indexed_vector.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/info.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/ipm.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/ipx_c.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/ipx_config.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/ipx_info.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/ipx_internal.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/ipx_parameters.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/ipx_status.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/iterate.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/kkt_solver_basis.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/kkt_solver_diag.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/kkt_solver.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/linear_operator.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/lp_solver.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/lu_factorization.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/lu_update.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/maxvolume.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/model.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/multistream.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/normal_matrix.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/power_method.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/sparse_matrix.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/sparse_utils.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/splitted_normal_matrix.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/starting_basis.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/symbolic_invert.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/timer.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/ipx" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/ipx/utils.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/basiclu_factorize.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/basiclu_get_factors.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/basiclu_initialize.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/basiclu_obj_factorize.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/basiclu_obj_free.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/basiclu_obj_get_factors.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/basiclu_obj_initialize.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/basiclu_obj_solve_dense.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/basiclu_obj_solve_for_update.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/basiclu_obj_solve_sparse.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/basiclu_obj_update.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/basiclu_object.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/basiclu_solve_dense.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/basiclu_solve_for_update.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/basiclu_solve_sparse.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/basiclu_update.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/basiclu.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/lu_def.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/lu_file.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/lu_internal.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/ipm/basiclu" TYPE FILE FILES "/root/cdev/manyhighs/highs/ipm/basiclu/lu_list.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/quantum" TYPE FILE FILES "/root/cdev/manyhighs/highs/quantum/HighsQubo.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/quantum" TYPE FILE FILES "/root/cdev/manyhighs/highs/quantum/HighsQuantumHeuristic.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs/quantum" TYPE FILE FILES "/root/cdev/manyhighs/highs/quantum/HighsQuantumOptions.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cli;libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/highs" TYPE FILE FILES "/root/cdev/manyhighs/build_on/HConfig.h")
endif()

