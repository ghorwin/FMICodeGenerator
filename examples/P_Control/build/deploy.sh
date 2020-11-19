#!/bin/bash

# script is supposed to be executed in /build directory

# remove target directory if it exists
if [ -d P_Control ]; then
  rm -rf P_Control 
fi &&

# remove target FMU if it exists
if [ -f P_Control.fmu ]; then
    rm P_Control.fmu 
fi &&

# create subdir and change into it
mkdir -p P_Control &&
cd P_Control &&

# create binary dir for Linux
mkdir -p binaries/linux64 &&

# copy shared library, we expect it to be already renamed correctly
cp ../../bin/release/P_Control.so binaries/linux64/P_Control.so &&
cp ../../data/modelDescription.xml . &&

# create zip archive
7za a ../P_Control.zip . | cat > /dev/null &&
cd .. && 
mv P_Control.zip P_Control.fmu &&
echo "Created P_Control.fmu" &&

# change working directory back to original dir
cd -

