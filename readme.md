# Coding Guidelines and Information

## Directory Structure

    bin     - batch/shell scripts to simplify/automate FMU generation
    data    - resources and template files
    doc     - documentation
    scripts - the actual python scripts
	tests   - holds autogenerate FMUs and co-simulation tests to check for compliance

## Coding Conventions

### Indentation

Only Tabs (usually displayed with 4 spaces)

### Code documentation

Python doc strings according to PEP 257.

### Variable and Function namings

- camel-case with capital first letter for class/type names
- camel-case with lower case first letter for member functions
- prefix `m_` for member variables


### Documentation

- external documentation (not in source code files) should go into the `doc` directory
- where appropriate, use markdown files  (extension `.md`)
- longer technical docs use Lyx (https://www.lyx.org/Home)
