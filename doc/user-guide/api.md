# Python API

To use the FMUCodeGenerator functionality from other software, you can use the Python-API provided by the Python library. Basically, you create an instance of class `FMIGenerator()`, specify its attributes and call the member function `generate()`. As simple as that :-)

```python
# import FMIGenerator class and data types
from FMIGenerator import *

# create instance of FMIGenerator class
fmiGen = FMIGenerator()

# specify attributes
fmiGen.modelName = "MyFirstFMU"
fmiGen.description = "My first auto-generated FMU. Awesome, right?"
fmiGen.targetDir = "../fmus" 
# 'targetDir' can be relative path to current working directory 
# or an absolute file path

# add variables to export
v = VarDef("InputVar1", "continuous", "input", "exact", "Real") 
# valueRef will be given automatically unless specified explicitely
v.startValue = 15
fmiGen.variables.append(v)

# now generate the FMU
fmiGen.generate()
```
