# FMU Compliance Checker Testing Procedure

The FMUs created by the FMIGenerator are only backbones and lack specific functionality. To test the correct export, we will follow this procedure:

1. define an FMU with given parameters and variables according to the defined test scenario (see below)
2. generate the FMU directory with the FMIGenerator
3. add C++-Code into FMU source stub
4. build and deploy `.fmu` file
5. run file through compliance checker

## Test Scenarios

Here is a list of test scenarios to test and demonstrate the functionality of the FMIGenerator. 

- [Stateless P-controller](p-controller.md): Tests the very basic functionality (if FMU is well formed and modelDescription is syntactically correct). No serialization is needed, so there cannot be anything wrong with that.
- [Stateless digital controller with switching delay](digital-controller.md): Tests serialization functionality for a model with an internal state (or local variable).
- [Lotka-Volterra (Predator-Prey) Model](lotka-volterra.md): Tests generation of state variables, derivatives, modelDescription formulation and serialization code.
