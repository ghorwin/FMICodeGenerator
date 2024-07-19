import argparse
import json
import jsonschema
import re
from pathlib import Path
import sys

class JSONError(Exception):
    pass

class ConsistencyError(Exception):
    pass

class JSONInputReader:

    def __stripFunctionDefinition(self, s):
        # Remove type hints
        noTypeHints = re.sub(':.*,', ' ', s)
        #noTypeHints = re.sub(':.*\x29', ' ', noTypeHints) # Replace `\)` with `\x29` to avoid deprecation warnings
        noTypeHints = re.sub(':.*\)', ' ', noTypeHints)
        noTypeHints = re.sub('->.*:', ':', noTypeHints)
        # Remove `def`, parentheses and colons
        noTypeHints = noTypeHints.replace("def", "").replace("(", " ").replace(")", " ").replace(",", " ").replace(":", "")
        return noTypeHints

    def __findFunctionDefinition(self, line):
        regexp = '^def.*:$'
        line = line.split('#')[0].strip()
        result = re.search(regexp, line)
        if result:
            noTypeHints = self.__stripFunctionDefinition(result.group())
            nameAndArguments = noTypeHints.split()
            # Discard internal/private functions
            if not nameAndArguments[0].startswith("_"):
                return {nameAndArguments[0] : len(nameAndArguments) - 1}
        return None

    def _readJSONFile(self, path):
        """Can raise FileNotFoundError"""
        inputSchemaPath = ((Path(__file__).parent) / "inputSchema.json").resolve().as_posix()
        with open(path) as jf, open(inputSchemaPath) as js:
            jsonInput = json.load(jf)
            jsonInputSchema = json.load(js)
            try:
                jsonschema.validate(instance=jsonInput, schema=jsonInputSchema)
            except jsonschema.SchemaError as e:
                raise self.JSONError(e)
            except jsonschema.ValidationError as e:
                raise JSONError(e)
        print(jsonInput)
        return jsonInput

    def _readPythonFile(self, path):
        """Can raise FileNotFoundError"""
        pyCode = ''
        pyFunctions = {}
        with open(path, 'r') as pf:
            # Read the source code line by line, so as to keep track of function definitions in a single pass
            for currentLine in pf:
                pyCode = pyCode + f"{currentLine}"
                defMatch = self.__findFunctionDefinition(currentLine.strip())
                if defMatch is not None:
                    pyFunctions.update(defMatch)
        return pyCode, pyFunctions

    def _checkVariableConsistency(self, jsonInput):
        """Checks that the variables declared in the JSON input are consistent:
            * variable names and value references are unique;
            * the start value has the type declared in the `typeID` attribute.
        
        Args:
            jsonInput: deserialized JSON input

        Returns:
            A dictionary mapping the variables declared in the JSON input to their causality string (one of
            `input`, `output`, `local`, `parameter`, `calculatedParameter`, `independent`).
        """
        typesMap = {'Real': float, 'Integer': int, 'String': str, 'Boolean': bool}
        varMap = {}
        valueRefList = []
        for var in jsonInput['variables']:
            # Fetch variable name and check uniqueness
            if var['name'] in varMap:
                raise ConsistencyError(f"Variable {var['name']} is defined more than once")
            varMap[var['name']] = var['causality']
            # Fetch valueRef and check uniqueness
            if 'valueRef' in var:
                if var['valueRef'] in valueRefList:
                    raise ConsistencyError(f"Value reference {var['valueRef']} is used more than once")
                valueRefList.append(var['valueRef'])
            # Check the type of the start value
            if type(var['startValue']) is not typesMap[var['typeID']]:
                raise ConsistencyError(f"Start value for variable {var['name']} is of type {type(var['startValue'])}, expected {var['typeID']}")
        return varMap
            
    def _checkFunctionConsistency(self, jsonInput, pyFunctions, varMap):
        """Checks that the functions declared in the JSON input and the Python source file are consistent:
            * each function declared in the JSON input exists in the Python source, with the same number of arguments;
            * function arguments declared in the JSON input are, either non-output variables declared in this file,
                or one of `start_time`, `stop_time`, `step_size`;
            * function outputs declared in the JSON input are output or local variables declared in this file.

        Args:
            jsonInput: deserialized JSON input
            pyFunctions: dictionary mapping the public functions declared in the Python source code to their number of
                arguments, as returned by :func:`_readPythonFile`
            varMap: dictionary mapping the variables declared in the JSON input to their causality string, as returned
                by :func:`_checkVariableConsistency`
        """
        varMap.update({'start_time' : 'input', 'stop_time' : 'input', 'step_size' : 'input'})
        for function in jsonInput['pythonFunctions'].values():
            for functionAttributes in function:
                print(functionAttributes)
                pythonFunctionName = functionAttributes['pythonName']
                # Check that the pythonName is actually the name of a function from the Python source
                if pythonFunctionName not in pyFunctions:
                    raise ConsistencyError(f"Function {pythonFunctionName} does not exist in the Python source file")
                # Check that the function has the right number of arguments
                if len(functionAttributes['arguments']) != pyFunctions[pythonFunctionName]:
                    raise ConsistencyError("Function {} should receive {} argument(s) but is given input {}"
                                        .format(pythonFunctionName,pyFunctions[pythonFunctionName],functionAttributes['arguments']))
                # Check that no argument has causality 'output'
                for functionArgument in functionAttributes['arguments']:
                    if functionArgument not in varMap:
                        raise ConsistencyError(f"Argument {functionArgument} of function {pythonFunctionName} does not exist")
                    if varMap[functionArgument] == 'output':
                        raise ConsistencyError(f"Output variable {functionArgument} cannot be used as an argument of function {pythonFunctionName}")
                # Check that the output is declared and has causality 'output' or 'local'
                outputVariable = functionAttributes['output']
                if outputVariable not in varMap:
                    raise ConsistencyError(f"Output {outputVariable} of function {pythonFunctionName} does not exist")
                if varMap[outputVariable] not in ['output', 'local']:
                    raise ConsistencyError(f"Variable {outputVariable} has causality {varMap[outputVariable]}, thus cannot be the output of function {pythonFunctionName}")

    def readInput(self, inputFilePath):
        modelInput = self._readJSONFile(inputFilePath)
        varList = self._checkVariableConsistency(modelInput)

        # Turn the path to the Python source, the Spycic library and the destination folder
        # from "relative to the JSON" to "absolute"
        baseFolderPath = Path(inputFilePath).parent
        pythonSourcePath = baseFolderPath / Path(modelInput['pythonSource'])
        modelInput['pythonSource'] = str(pythonSourcePath.resolve())
        if 'spycicLocation' in modelInput:
            spycicPath = baseFolderPath / Path(modelInput['spycicLocation'])
        else:
            spycicPath = baseFolderPath / 'spycic'
            print(f"WARNING: path to Spycic not provided, defaulting to {str(spycicPath.resolve())}")
        modelInput['spycicLocation'] = str(spycicPath.resolve())
        if 'fmuDestination' in modelInput:
            fmuPath = baseFolderPath / Path(modelInput['fmuDestination'])
        else:
            fmuPath = baseFolderPath
        modelInput['fmuDestination'] = str(fmuPath.resolve())

        # Add a default description if necessary
        if 'description' not in modelInput or modelInput['description'] == "":
            modelInput["description"] = f"Model {modelInput['modelName']}"

        pyCode, pyFunctions = self._readPythonFile(pythonSourcePath)
        self._checkFunctionConsistency(modelInput, pyFunctions, varList)

        modelInput['pythonSource'] = pyCode
        return modelInput

# Run as first-level code using `python3 JSONInputReader.py path/to/the/input/file.json`
if __name__ == '__main__':
    parser = argparse.ArgumentParser("JSONInputReader.py")
    parser.add_argument("inputFile", help="Relative or absolute path of the input JSON file")
    inputFilePath = parser.parse_args().inputFile
    reader = JSONInputReader()
    sys.exit(reader.readInput(inputFilePath))