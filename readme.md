# About the FMI Code Generator

## What is this FMI/FMU stuff?

FMU stands for _Functional Mockup Unit_ and FMI for _Functional Mockup Interface_. The latter is an industry standard
for simulation model runtime coupling, and basically defines an API and a meta data description file and directory structure for model exchange: see [FMI-Standard webpage](https://fmi-standard.org) for details.

## The Motivation

When you want an efficient FMU slave, there's probably no way around a native C/C++ implementation. However, implementing the C interface functions, the data handling, input/output variable handling and advanced features like **saving and restoring the FMU state** is not so simple and straight-forward.

However, the process of setting up the FMU (core files, `modelDescription.xml`, directory structure) is pretty similar for most projects and can be automated with a configurable code generator - hence this project.

## The (anticipated) use of the FMI Code Generator

### Create a fully working FMU source code template

Creating the barebone of an FMU should be as simple as that:

1. clone this repository
2. run the script `generate.bat` or `generate.sh`

    > # this will generate a directory structure TestFMI01 within 
    > # your current working directory
    > ~/git/FMICodeGenerator/bin/generate.sh TestFMI01 --description "My First Test"

3. give the relevant information (model name, list of input and output vars, parameters, integration states etc.)

Once the generator has finished, you have a fully working FMU source code with matching `modelDescription.xml` and can build it cross-platform with a CMake-based build system.

### Develop FMU-specific functionality

The template directory structure contains build system files for CMake and Qt-qmake. With CMake, you can easily generate makefiles for various compilers and development environments. With the pro-files you can directly start developing with Qt Creator (even though the FMU code itself is plain C/C++ code without Qt dependencies).

### Generate fmu and deploy

The template directory structure contains a deployment script/batch file (either `<FmuModelName>/build/deploy.sh` or `<FmuModelName>/build/deploy.bat`).

You may want to adjust the `deploy.sh` script to add, for example, own resources.

Deployment works as follows (for Linux/Unix/Mac):

```bash
# change into generated directory structure
cd <FmuModelName>/build
# build the FMU in release mode
./build.sh release
# deploy the FMU, e.g. package the FMU in the zipped directory structure
./deploy.sh
```

# Information and Coding Guidelines

## Directory Structure

    bin                 - batch/shell scripts to simplify/automate FMU generation
    data                - resources and template files
    doc                 - documentation, also includes examples
    examples            - example directory structures (this is what the FMI generator should produce)
    scripts             - the actual python scripts
    scripts/third_party - external library and scripts
    third_party         - external tools like the compliance checker

## Coding Conventions

This applies to the Python-code in this project. However, the generated C/C++ code follows similar conventions.

### Indentation

Only Tabs (usually displayed with 4 spaces)

### Code documentation

Python doc strings according to PEP 257 (see https://www.python.org/dev/peps/pep-0257).

### Variable and Function namings

- camel-case with capital first letter for class/type names
- camel-case with lower case first letter for member functions
- underscore-names for free functions (should be limited)

### Documentation

- external documentation (not in source code files) should go into the `doc` directory
- where appropriate, use markdown files  (extension `.md`)
- longer technical docs use Lyx/Latex (https://www.lyx.org/Home)

### Example

```python

class ExampleClass:
    """This class serves as coding style and documentation style example.
    Class names (and type names in general) should be in camel-case and start with a capital letter.
    """
    
    def __init__(self):
        """Construction, initializes member variables.
        Note prefix m_ of member variables!
        """
        
        self.m_someDataMember = ""
        self.m_someList = []
        
    def doSomething(self, firstNumber, someString):
        """Member function names should be in camel case, starting with a lower-case letter.
        Function documentation should include documentation of arguments.
        
        Arguments:
        firstNumber -- A number between 0 and 10
        someString -- A descriptive string or...
        """
        
        # document pieces of code with simple comments
        print someString
        print ("{} with {} values").format(someString, firstNumber)
```
   
