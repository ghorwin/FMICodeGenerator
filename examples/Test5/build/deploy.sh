#!/bin/bash

# script is supposed to be executed in /build directory

# remove target directory if it exists
if [ -d Test5 ]; then
  rm -rf Test5 
fi &&

# remove target FMU if it exists
if [ -f Test5.fmu ]; then
    rm Test5.fmu 
fi &&

# create subdir and change into it
mkdir -p Test5 &&
cd Test5 &&

# create binary dir for Linux
mkdir -p binaries/linux64 &&

# copy shared library, we expect it to be already renamed correctly
cp ../../bin/release/Test5.so binaries/linux64/Test5.so &&
cp ../../data/modelDescription.xml . &&

# create zip archive
7za a ../Test5.zip . | cat > /dev/null &&
cd .. && 
mv Test5.zip Test5.fmu &&
echo "Created Test5.fmu" &&

# change working directory back to original dir
cd -

