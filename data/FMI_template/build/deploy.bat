@echo off
:: script is supposed to be executed in /build directory

if exist ..\bin\release_x64\FMI_template.dll goto DLL_EXISTS
echo "ERROR: File FMI_template.dll expected in directory ..\bin\release_x64\FMI_template.dll, but does not exist.
exit /b 1
:DLL_EXISTS

:: remove target directory if it exists
if not exist FMI_template goto DIRECTORY_CLEAN
echo Removing existing directory 'FMI_template'
rd /S /Q "FMI_template"
:DIRECTORY_CLEAN

:: remove target FMU if it exists
if not exist FMI_template.fmu goto FMU_REMOVED
echo Removing existing FMU file 'FMI_template.fmu'
del /F /S /Q "FMI_template.fmu"
:FMU_REMOVED

::create subdir and change into it
mkdir FMI_template

cd FMI_template

:: create binary dir for Windows
mkdir binaries\win64

:: copy shared library, we expect it to be already renamed correctly
xcopy ..\..\bin\release_x64\FMI_template.dll binaries\win64\
xcopy ..\..\data\modelDescription.xml .
echo Created FMU directory structure

::change working directory back to original dir
cd ..

::create zip archive
echo Creating archive 'FMI_template.zip'
cd FMI_template
7za a ../FMI_template.zip .
cd ..

echo Renaming archive to 'FMI_template.fmu'
rename FMI_template.zip FMI_template.fmu

:: all ok
exit /b 0
