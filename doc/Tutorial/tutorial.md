# Concept: FMI Beginners Tutorial for Modelica Conference 2025

- **Title:** FMI Beginners Tutorial - Writing an FMU in C/C++
- **Suggested duration of the tutorial:** 2 hours
- **Presenter(s) name(s) and affiliation(s)**: Dr. Andreas Nicolai, Umwelt- und Ingenieurtechnik GmbH Dresden

## Abstract

Purpose of the tutorial is to show the creation of a ModelExchange and a Co-Simulation FMU for a simple
physical soil collector model to be used in domestic low energy district network.
The model will be shortly explained and a brief overview of the coupled simulation scenario will be given.
We'll start by designing a ModelExchange-FMU, defining interface variables (inputs and outputs, and parameters) and 
writing the `modelDescription.xml` file. 
Next is a short recap on shared library programming on Windows, Mac and Linux. A CMake build system is presented with a test 
shared library and program, for each participant to test their tool chain.  We then start writing the C-code for the 
ModelExchange FMU v2.0 with only the mandatory functions. The FMU library will be build and we compose the FMU by
assembling the files into the directory structure and zipping the FMU together. Finally, the FMU will be tested in OpenModelica with a prepared test model. We then move to FMI for Co-Simulation, where we just introduce the alternative functions and a simple time integration routine.
The FMI is generated again and tested with a prepared co-simulation scenario using MasterSim or any other FMI master. Finally, the automation of generating barebone c-code and build system/deployment files with the FMICodeGenerator tool is demonstrated.

## Expected experience of participants

Participants should have a basic understanding of FMI-concepts and ME/CS modes. Also, they should know C/C++ programming at beginners level and should know their development environment.

## Software requirements

- C/C++ compiler: on Windows MinGW or Visual Studio is recommended (I use MinGW32-8.1 x64); on Linux gcc/clang; on Mac default compiler
- CMake
- MasterSim (OpenSource) or any other FMI Co-Simulation-Master
- OpenModelica (OpenSource) or any other FMI ModelExchange-Master
- (optional) FMICodeGenerator (OpenSource)

