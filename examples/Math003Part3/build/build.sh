#!/bin/bash


# Build script for building FMU

# Command line options:
#   [reldeb|release|debug]		build type
#   [2 [1..n]]					cpu count
#   [gcc|icc]					compiler
#   [off|gprof]					gprof (includes gcc)
#   [off|threadChecker]			threadchecker (includes icc)
#   [off|omp]					openmp (gcc and icc)
#   [verbose]					enable cmake to call verbose makefiles

CMAKELISTSDIR=$(pwd)/../projects/cmake
BUILDDIR="bb"



# set defaults
CMAKE_BUILD_TYPE=" -DCMAKE_BUILD_TYPE:STRING=RelWithDebInfo"
MAKE_CPUCOUNT="2"
BUILD_DIR_SUFFIX="gcc"
COMPILER=""
SKIP_TESTS="false"

# parse parameters, except gprof and threadchecker
for var in "$@"
do

	if [[ $var = "--help" ]];
	then
		echo "Command line options:"
		echo "  [reldeb|release|debug]      build type"
		echo "  [2 [1..n]]                  cpu count"
		echo "  [gcc|icc]                   compiler"
		echo "  [off|gprof]                 gprof (includes gcc)"
		echo "  [off|threadChecker]         threadchecker (includes icc)"
		echo "  [off|omp]                   openmp (gcc and icc)"
		echo "  [verbose]                   enable cmake to call verbose makefiles"

		exit
	fi

    if [[ $var = *[[:digit:]]* ]];
    then
		MAKE_CPUCOUNT=$var
		echo "Using $MAKE_CPUCOUNT CPUs for compilation"
    fi

    if [[ $var = "omp"  ]];
    then
		CMAKE_OPTIONS="$CMAKE_OPTIONS -DUSE_OMP:BOOL=ON"
		echo "Using Open MP compile flags"
    fi

    if [[ $var = "debug"  ]];
    then
		CMAKE_BUILD_TYPE=" -DCMAKE_BUILD_TYPE:STRING=Debug"
		echo "Debug build..."
    fi

    if [[ $var = "release"  ]];
    then
		CMAKE_BUILD_TYPE=" -DCMAKE_BUILD_TYPE:STRING=Release"
		echo "Release build..."
    fi

    if [[ $var = "reldeb"  ]];
    then
		CMAKE_BUILD_TYPE=" -DCMAKE_BUILD_TYPE:STRING=RelWithDebInfo"
		echo "RelWithDebInfo build..."
    fi

    if [[ $var = "icc"  && $COMPILER = "" ]];
    then
		COMPILER="icc"
		BUILD_DIR_SUFFIX="icc"
		echo "Intel compiler build..."
	    # export intel compiler path
	    CMAKE_COMPILER_OPTIONS="-DCMAKE_C_COMPILER=icc -DCMAKE_CXX_COMPILER=icc"
	  fi

    if [[ $var = "gcc"  && $COMPILER = "" ]];
    then
		COMPILER="gcc"
		BUILD_DIR_SUFFIX="gcc"
		echo "GCC compiler build..."
		CMAKE_COMPILER_OPTIONS=""
	  fi

    if [[ $var = "verbose"  ]];
  	then
		CMAKE_OPTIONS="$CMAKE_OPTIONS -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"
	  fi

done


# override compiler options
for var in "$@"
do

    if [[ $var = "gprof" ]];
    then
		COMPILER="gcc"
		BUILD_DIR_SUFFIX="gcc"
		CMAKE_COMPILER_OPTIONS="-DCMAKE_CXX_FLAGS="'-pg'" -DCMAKE_EXE_LINKER_FLAGS="'-pg'""
		echo "Gprof build, forcing GCC build..."
    fi

    if [[ $var = "threadChecker"  ]];
    then
		COMPILER="icc"
		BUILD_DIR_SUFFIX="icc"
		echo "Using Threadchecker, forcing Intel compiler build..."
	    # export intel compiler path
	    CMAKE_COMPILER_OPTIONS="-DCMAKE_C_COMPILER=icc -DCMAKE_CXX_COMPILER=icc -DUSE_THREAD_CHECKER:BOOL=ON"
	fi

done


# create build dir if not exists
BUILDDIR=$BUILDDIR-$BUILD_DIR_SUFFIX
if [ ! -d $BUILDDIR ]; then
    mkdir -p $BUILDDIR
fi

cd $BUILDDIR && cmake $CMAKE_OPTIONS $CMAKE_BUILD_TYPE $CMAKE_COMPILER_OPTIONS $CMAKELISTSDIR && make -j$MAKE_CPUCOUNT &&
cd $CMAKELISTSDIR &&
mkdir -p ../bin/release &&
if [ -e $BUILDDIR/MasterSimulator/MasterSimulator ]; then
  echo "*** Copying MasterSimulator to bin/release ***" &&
  cp $BUILDDIR/MasterSimulator/MasterSimulator ../../bin/release/MasterSimulator
fi &&
if [ -e $BUILDDIR/MasterSimulatorUI/MasterSimulatorUI ]; then
  echo "*** Copying MasterSimulatorUI to bin/release ***" &&
  cp $BUILDDIR/MasterSimulatorUI/MasterSimulatorUI ../../bin/release/MasterSimulatorUI
fi &&
if [ -e $BUILDDIR/MasterSimulatorUI/MasterSimulatorUI.app ]; then
  if [ -e ../../bin/release/MasterSimulatorUI.app ]; then
    rm -rf ../../bin/release/MasterSimulatorUI.app
  fi &&
  echo "*** Copying MasterSimulatorUI.app to bin/release ***" &&
  cp -r $BUILDDIR/MasterSimulatorUI/MasterSimulatorUI.app ../../bin/release/MasterSimulatorUI.app
fi &&

echo "*** Copying TestFMUs to bin/release ***" &&
if [ -e $BUILDDIR/MasterSimulatorUI/MasterSimulatorUI.app ]; then
  cp $BUILDDIR/Math003Part1/libMath003Part1.dylib ../../bin/release/libMath003Part1.dylib &&
  cp $BUILDDIR/Math003Part2/libMath003Part2.dylib ../../bin/release/libMath003Part2.dylib &&
  cp $BUILDDIR/Math003Part3/libMath003Part3.dylib ../../bin/release/libMath003Part3.dylib &&
  cp $BUILDDIR/LotkaVolterraPrey/libLotkaVolterraPrey.dylib ../../bin/release/libLotkaVolterraPrey.dylib &&
  cp $BUILDDIR/LotkaVolterraPredator/libLotkaVolterraPredator.dylib ../../bin/release/libLotkaVolterraPredator.dylib
else
  cp $BUILDDIR/Math003Part1/libMath003Part1.so ../../bin/release/libMath003Part1.so &&
  cp $BUILDDIR/Math003Part2/libMath003Part2.so ../../bin/release/libMath003Part2.so &&
  cp $BUILDDIR/Math003Part3/libMath003Part3.so ../../bin/release/libMath003Part3.so &&
  cp $BUILDDIR/LotkaVolterraPrey/libLotkaVolterraPrey.so ../../bin/release/libLotkaVolterraPrey.so &&
  cp $BUILDDIR/LotkaVolterraPredator/libLotkaVolterraPredator.so ../../bin/release/libLotkaVolterraPredator.so
fi &&

echo "*** Build MasterSimulator ***" &&
if [[ $SKIP_TESTS = "false"  ]];
then
./run_tests.sh
fi

echo "*** Generating TEST FMUs ***" &&
(cd ../../TestFMUs;./generate_FMUs.sh)

