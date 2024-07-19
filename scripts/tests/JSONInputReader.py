# Run with `pytest <thisfile.py>`; use option `-s` to disable
# per-test stdout capture (for debugging purposes).

import pytest
from scripts.jsonimport.JSONInputReader import *
#from PythonFMUGenerator.jsonimport import JSONInputReader
import sys
from pathlib import Path

reader = JSONInputReader()

def runFrom(path):
    # Make all paths relative to the path to this file instead of relying
    # on the path from which the file is run
    realPath = (Path(__file__).parent / path).resolve()
    reader.readInput(realPath)

class TestInvalidJSON:

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            runFrom('test/nice.py')

    def test_empty_model_name(self):
        with pytest.raises(JSONError):
            runFrom('InvalidJSON/emptyModelName.json')

    def test_empty_pythonSource(self):
        with pytest.raises(JSONError):
            runFrom('InvalidJSON/emptyPythonSource.json')

    def test_empty_variables(self):
        with pytest.raises(JSONError):
            runFrom('InvalidJSON/emptyVariables.json')

    def test_lacking_model_name(self):
        with pytest.raises(JSONError):
            runFrom('InvalidJSON/lackingModelName.json')

    def test_lacking_python_functions(self):
        with pytest.raises(JSONError):
            runFrom('InvalidJSON/lackingPythonFunctions.json')

    def test_lacking_pythonSource(self):
        with pytest.raises(JSONError):
            runFrom('InvalidJSON/lackingPythonSource.json')

    def test_lacking_variable_causality(self):
        with pytest.raises(JSONError):
            runFrom('InvalidJSON/lackingVariableCausality.json')

    def test_lacking_variable_initial(self):
        with pytest.raises(JSONError):
            runFrom('InvalidJSON/lackingVariableInitial.json')

    def test_lacking_variable_name(self):
        with pytest.raises(JSONError):
            runFrom('InvalidJSON/lackingVariableName.json')

    def test_lacking_variables(self):
        with pytest.raises(JSONError):
            runFrom('InvalidJSON/lackingVariables.json')

    def test_lacking_variable_typeID(self):
        with pytest.raises(JSONError):
            runFrom('InvalidJSON/lackingVariableTypeID.json')

    def test_lacking_variable_variability(self):
        with pytest.raises(JSONError):
            runFrom('InvalidJSON/lackingVariableVariability.json')

class TestInconsistentVariables:

    def test_mistyped_start_value_boolean(self):
        with pytest.raises(ConsistencyError, match='Start value for variable badlyTyped'):
            runFrom('InconsistentVariables/mistypedStartValueBoolean.json')

    def test_mistyped_start_value_integer(self):
        with pytest.raises(ConsistencyError, match='Start value for variable badlyTyped'):
            runFrom('InconsistentVariables/mistypedStartValueInteger.json')

    def test_mistyped_start_value_real(self):
        with pytest.raises(ConsistencyError, match='Start value for variable badlyTyped'):
            runFrom('InconsistentVariables/mistypedStartValueReal.json')

    def test_mistyped_start_value_string(self):
        with pytest.raises(ConsistencyError, match='Start value for variable badlyTyped'):
            runFrom('InconsistentVariables/mistypedStartValueString.json')

    def test_multiple_definition(self):
        with pytest.raises(ConsistencyError, match='Variable definedTwice is defined more than once'):
            runFrom('InconsistentVariables/multipleDefinition.json')

    def test_multiple_valueRef(self):
        with pytest.raises(ConsistencyError, match='Value reference 42 is used more than once'):
            runFrom('InconsistentVariables/multipleValueRef.json')

class TestInconsistentFunctions:

    def test_bad_number_of_variables(self):
        with pytest.raises(ConsistencyError, match='init should receive 0 argument'):
            runFrom('InconsistentFunctions/badNumberOfVariables.json')

    def test_bad_number_of_variables2(self):
        with pytest.raises(ConsistencyError, match='do_step should receive 2 argument'):
            runFrom('InconsistentFunctions/badNumberOfVariables2.json')

    def test_missing_argument(self):
        with pytest.raises(ConsistencyError, match='not_a_variable'):
            runFrom('InconsistentFunctions/missingArgument.json')

    def test_missing_function(self):
        with pytest.raises(ConsistencyError, match='initialize does not exist'):
            runFrom('InconsistentFunctions/missingFunction.json')

    def test_missing_output(self):
        with pytest.raises(ConsistencyError, match='not_an_output.*does not exist'):
            runFrom('InconsistentFunctions/missingOutput.json')

    def test_mistyped_argument(self):
        with pytest.raises(ConsistencyError, match='Output variable tempOut1.*argument'):
            runFrom('InconsistentFunctions/mistypedArgument.json')

    def test_mistyped_output(self):
        with pytest.raises(ConsistencyError, match='Variable tempIn.*input.*output of function do_step'):
            runFrom('InconsistentFunctions/mistypedOutput.json')

class TestValidInput:

    def test_valid_input(self):
        runFrom('testCode.json')