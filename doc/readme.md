# Basic concepts

Anticipated workflow:

1. call `generate.py` (or `generate.sh` or `generate.bat`) to create a basic directory
   structure for FMU development with initial source code and `modelDescription.xml` file
2. start editing C/C++ code and testing it (use prepared Qt creator project file or cmake based build)
3. generate FMU by calling `deploy.py` (or `deploy.sh` or `deploy.bat`) to create the FMU
