#!/bin/bash

# script is supposed to be executed in /build directory

# remove target directory if it exists
if [ -d Math003Part3 ]; then
  rm -rf Math003Part3 &&
fi

# remove target FMU if it exists
if [ -f ../Math003Part3.fmu ]; then
    rm ../Math003Part3.fmu &&
fi

# create subdir and change into it
mkdir -p Math003Part3 &&
cd Math003Part3 &&

# create binary dir for Linux
mkdir -p binaries/linux64 &&

# copy shared library, we expect it to be already renamed correctly
cp ../../bin/release/libMath003Part1.so binaries/linux64/Math003Part3.so &&
cp ../../data/modelDescription.xml . &&

# create zip archive
7za a ../Math003Part3.zip . | cat > /dev/null &&
cd .. && 
mv Math003Part3.zip Math003Part3.fmu &&
echo "Created Math003Part3.fmu" &&

# change working directory back to original dir
cd -

