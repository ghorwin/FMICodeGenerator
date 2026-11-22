# Coding Conventions

This applies to the Python-code in this project. However, the generated C/C++ code follows similar conventions.

## Indentation

Only Tabs (usually displayed with 4 spaces)

## Code documentation

Python doc strings according to PEP 257 (see https://www.python.org/dev/peps/pep-0257).

## Variable and Function namings

- camel-case with capital first letter for class/type names
- camel-case with lower case first letter for member functions
- underscore-names for free functions (should be limited)

### Example

```python

class ExampleClass:
    """This class serves as coding style and documentation style example.
    Class names (and type names in general) should be in camel-case and start with 
    a capital letter.
    """
    
    def __init__(self):
        """Construction, initializes member variables.
        Note: member variables are camel-case as well, starting with lower-case 
              letter. No prefix is needed, since 'self.' is already identifying 
              variables as member variables.
        """
        
        self.someDataMember = ""
        self.someList = []
        
    def doSomething(self, firstNumber, someString):
        """Member function names should be in camel case, starting with a 
        lower-case letter. Function documentation should include documentation 
        of arguments as follows.
        
        Arguments:
        firstNumber -- A number between 0 and 10
        someString -- A descriptive string or...
        """
        
        # document pieces of code with simple comments
        print someString
        print ("{} with {} values").format(someString, firstNumber)
```
   
## Documentation

- external documentation (not in source code files) should go into the `doc` directory
- where appropriate, use markdown files  (extension `.md`)
- longer technical docs use Lyx/Latex (https://www.lyx.org/Home)

