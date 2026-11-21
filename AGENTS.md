# AGENTS.md

This repo is a Python/PyQt5 **code generator**: its product is a generated FMU (FMI2 C++ source tree), not the repo itself. The generator core is `scripts/FMIGenerator.py` (classes `FMIGenerator`, `VarDef`); `generate()` copies `data/FMI_template` to `<targetDir>/<modelName>`, renames files and substitutes the placeholder string `FMI_template` with the model name.

## Entry points & commands

- GUI wizard: `python scripts/main.py` (needs a display; PyQt5).
- GUI start page: "Create a new FMU project" or "Open an existing FMU project". Opening one skips the basic-properties page and runs `FMIGenerator.update()` instead of `generate()`.
- CLI, new project: `python scripts/commandLineGenerator.py <modelName> --description "..." [--target-dir DIR] [--input vars.input] [--no-build] [--overwrite]`.
- CLI, update an existing project: `python scripts/commandLineGenerator.py --update <projectDir> [--no-build]`. This reads `<projectDir>/<modelName>.input`.
- To script generation with variables: instantiate `FMIGenerator`, append `VarDef(name, variability, causality, initial, typeID)` entries to `fmiGenerator.variables`, and call `generate()` or `update(projectDir)`.

## Setup

- Python 3.7+; `pip install -r requirements.txt` (PyQt5, send2trash).
- `pyuic5`/`pyrcc5` (pyqt5-dev-tools / PyQt5 package) are needed to regenerate UI code (below).
- No linter, formatter, typechecker, CI, or test framework exists in this repo. Don't assume one.

## Generated code in-repo — do not edit by hand

`scripts/Ui_*.py` and `scripts/FMIGenerator_rc.py` are generated from `scripts/ui/*.ui` and `scripts/ui/FMIGenerator.qrc`. After changing any `.ui` or `.qrc` file, run `scripts/ui/update.sh` to regenerate them.

## Template & placeholder conventions

- `data/FMI_template/` is the FMU source template. Who owns which file in a generated project:
  - Generator-owned, overwritten on every `update()` (the old versions are first copied to `<project>/.backup/<timestamp>/`): `data/modelDescription.xml`, `src/<model>_generated.h` (value-ref defines `FMI_INPUT_x`/`FMI_OUTPUT_x`/`FMI_PARA_x`/`FMI_LOCAL_x`, `struct FMIVariables`), `src/<model>_generated.cpp` (GUID, `InstanceData::create()`, `initFMIVariables()`, `readFMIVariables()`, `writeFMIVariables()`, and the generic FMU-state serialization `computeFMUStateSize()`/`serializeFMUstate()`/`deserializeFMUstate()`), and `<model>.input`. `_generated.h` also provides the `SERIALIZE`/`DESERIALIZE` macros.
  - User-owned, created once and never touched again: `src/<model>.h/.cpp`, `CMakeLists.txt`, `<model>.pro`, `build/*`. The user code holds the model-specific state in three hooks that the generated serialization calls: `userStateSize()`, `serializeUserState(char *&)` and `deserializeUserState(const char *&)`. The user data is written last, and the generated code checks that the byte count matches `m_fmuStateSize`. User headers declare both the generated and the hook member functions, so their signatures must stay stable.
  - The placeholders in `FMI_template_generated.*` and `modelDescription.xml` are `$$name$$` strings, filled in by `writeGeneratedFiles()`.
  - `update()` checks the user `.cpp` for definitions that are now generated (`findGeneratedDefinitionsInUserCode()`): GUID, `create()`, and the state functions. A project with no `_generated.h`, or with `#define FMI_` in the user `.cpp`, counts as legacy (generator <= 1.3). In both cases `update()` still writes the generated files, prints the manual migration steps (`printMigrationInstructions()`) and skips the test build.
- The folder/file name `FMI_template` is a hardcoded placeholder string (`TEMPLATE_FOLDER_NAME` in `scripts/FMIGenerator.py`); renaming it requires updating that constant and the rename logic in `copyTemplateDirectory()`.
- `data/FMI_template/build/build_VC_x64.bat` assumes Visual Studio 2022. For other VC versions, copy the matching `build_VC_x64_vc2015/2019/2022.bat` over it **before** generating an FMU (generation copies the template as-is).

## `.input` files

The project file `<projectDir>/<modelName>.input` is a JSON file (shape of `VarDef.toJson()`) holding the model name, the description and the variables. It is written inside the project directory, and the assigned value references are saved in it so they stay stable across updates. `findProjectInputFile()` also finds the legacy location `<projectDir>/../<dirname>.input`. Examples: `examples/P_Control/P_Control.input`, `examples/*.input`. When adding fields to `VarDef`, keep `toJson()`/`varDefFromJson()` in sync with this format.

## Verifying generated code

There is no automated test suite. The manual check path:

1. `data/check/` contains a hand-built `RealInputTest` project plus `input.tsv` for the FMI compliance checker.
2. Unzip `third_party/FMUChecker-2.0.4-linux64.zip` (win64 variant also present) to get `fmuCheck.linux64`.
3. From `data/check/`: `./fmuCheck.linux64 -f -i input.tsv -o output.tsv ../RealInputTest/build/RealInputTest.fmu`.

`examples/P_Control` is a reference output of the current generator, with user code added. `examples/Test5` is a legacy-layout project. To test updates: copy `examples/P_Control` to a scratch directory, edit its `.input` file, run `--update`, then check that `src/P_Control.cpp/.h` are byte-identical and that the build succeeds.
