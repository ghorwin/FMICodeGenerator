# AGENTS.md

This repo is a Python/PyQt5 **code generator**: its product is a generated FMU (FMI2 C++ source tree), not the repo itself. The generator core is `scripts/FMIGenerator.py` (classes `FMIGenerator`, `VarDef`); `generate()` copies `data/FMI_template` to `<targetDir>/<modelName>`, renames files and substitutes the placeholder string `FMI_template` with the model name.

## Entry points & commands

- GUI wizard: `python scripts/main.py` (needs a display; PyQt5).
- CLI (minimal, model name + description only, no variables): `python scripts/commandLineGenerator.py <modelName> --description "..."`.
- To script generation with variables: instantiate `FMIGenerator`, append `VarDef(name, variability, causality, initial, typeID)` entries to `fmiGenerator.variables`, call `generate()` (see commented test block in `commandLineGenerator.py`).

## Setup

- Python 3.7+; `pip install -r requirements.txt` (PyQt5, send2trash).
- `pyuic5`/`pyrcc5` (pyqt5-dev-tools / PyQt5 package) are needed to regenerate UI code (below).
- No linter, formatter, typechecker, CI, or test framework exists in this repo. Don't assume one.

## Generated code in-repo — do not edit by hand

`scripts/Ui_*.py` and `scripts/FMIGenerator_rc.py` are generated from `scripts/ui/*.ui` and `scripts/ui/FMIGenerator.qrc`. After changing any `.ui` or `.qrc` file, run `scripts/ui/update.sh` to regenerate them.

## Template & placeholder conventions

- `data/FMI_template/` is the FMU source template. The folder/file name `FMI_template` is a hardcoded placeholder string (`TEMPLATE_FOLDER_NAME` in `scripts/FMIGenerator.py`); renaming it requires updating that constant and the rename logic in `copyTemplateDirectory()`.
- `data/FMI_template/build/build_VC_x64.bat` assumes Visual Studio 2022. For other VC versions, copy the matching `build_VC_x64_vc2015/2019/2022.bat` over it **before** generating an FMU (generation copies the template as-is).

## `.input` files

After generation, the generator writes `<targetDir>/<modelName>.input` — a JSON file (shape of `VarDef.toJson()`) used by the wizard to re-populate fields. Examples: `examples/*.input`. When adding fields to `VarDef`, keep `toJson()`/`varDefFromJson()` in sync with this format.

## Verifying generated code

There is no automated test suite. The manual check path:

1. `data/check/` contains a hand-built `RealInputTest` project plus `input.tsv` for the FMI compliance checker.
2. Unzip `third_party/FMUChecker-2.0.4-linux64.zip` (win64 variant also present) to get `fmuCheck.linux64`.
3. From `data/check/`: `./fmuCheck.linux64 -f -i input.tsv -o output.tsv ../RealInputTest/build/RealInputTest.fmu`.

`examples/P_Control` and `examples/Test5` are reference outputs of what the generator should produce.
