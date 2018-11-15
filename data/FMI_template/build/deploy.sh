#!/bin/bash

# script is supposed to be executed in /build directory

# remove target directory if it exists
if [ -d FMI_template ]; then
  rm -rf FMI_template 
fi &&

# remove target FMU if it exists
if [ -f FMI_template.fmu ]; then
    rm FMI_template.fmu 
fi &&

# create subdir and change into it
mkdir -p FMI_template &&
cd FMI_template &&

# create binary dir for Linux
mkdir -p binaries/linux64 &&

# copy shared library, we expect it to be already renamed correctly
cp ../../bin/release/FMI_template.so binaries/linux64/FMI_template.so &&
cp ../../data/modelDescription.xml . &&

# create zip archive
7za a ../FMI_template.zip . | cat > /dev/null &&
cd .. && 
mv FMI_template.zip FMI_template.fmu &&
echo "Created FMI_template.fmu" &&

# change working directory back to original dir
cd -

