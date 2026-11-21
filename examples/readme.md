# Examples

This directory contains examples for generated FMUs source code, associated files and scripts. 
Added own code is indicatd by comments.


## P_Control

A simple example (also used in the tutorial). Generated with the current project layout: the project file
`P_Control/P_Control.input` lives inside the project directory, generated code is in
`src/P_Control_generated.h/.cpp`, and the controller code was added to `src/P_Control.cpp`.
Open the directory in the wizard ("Open an existing FMU project") or run
`python scripts/commandLineGenerator.py --update examples/P_Control` to update it.

Note: `P_Control.fmu` was built from the previous version of this example.

## Test5

Another simple controller, turns a heating on when 
the available energy generation rate exceeds a certain limit.

Thanks to Lisa for providing the FMU example.

This example uses the old project layout (FMICodeGenerator <= 1.3, no `_generated` files).

## *.input files

`P_Control_2inputs.input`, `TestWithOutputs.input` and `TestWithoutOutputs.input` are variable definitions
that can be used to create new projects, e.g.
`python scripts/commandLineGenerator.py --input examples/TestWithOutputs.input --target-dir /tmp`.
