#!/bin/bash

# script is supposed to be executed in /build directory

# remove target directory if it exists
if [ -d RealInputTest ]; then
  rm -rf RealInputTest 
fi &&

# remove target FMU if it exists
if [ -f RealInputTest.fmu ]; then
    rm RealInputTest.fmu 
fi &&

# create subdir and change into it
mkdir -p RealInputTest &&
cd RealInputTest &&

# create binary dir for Linux
mkdir -p binaries/linux64 &&

# copy shared library, we expect it to be already renamed correctly
cp ../../bin/release/RealInputTest.so binaries/linux64/RealInputTest.so &&
cp ../../data/modelDescription.xml . &&

# create zip archive
7za a ../RealInputTest.zip . | cat > /dev/null &&
cd .. && 
mv RealInputTest.zip RealInputTest.fmu &&
echo "Created RealInputTest.fmu" &&

# change working directory back to original dir
cd -

