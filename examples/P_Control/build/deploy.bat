@echo off
:: script is supposed to be executed in /build directory

if exist ..\bin\release_x64\P_Control.dll goto DLL_EXISTS
echo "ERROR: File P_Control.dll expected in directory ..\bin\release_x64\P_Control.dll, but does not exist.
exit /b 1
:DLL_EXISTS

:: remove target directory if it exists
if not exist P_Control goto DIRECTORY_CLEAN
echo Removing existing directory 'P_Control'
rd /S /Q "P_Control"
:DIRECTORY_CLEAN

:: remove target FMU if it exists
if not exist P_Control.fmu goto FMU_REMOVED
echo Removing existing FMU file 'P_Control.fmu'
del /F /S /Q "P_Control.fmu"
:FMU_REMOVED

::create subdir and change into it
mkdir P_Control

cd P_Control

:: create binary dir for Windows
mkdir binaries\win64

:: copy shared library, we expect it to be already renamed correctly
xcopy ..\..\bin\release_x64\P_Control.dll binaries\win64\
xcopy ..\..\data\modelDescription.xml .
echo Created FMU directory structure

::change working directory back to original dir
cd ..

::create zip archive
echo Creating archive 'P_Control.zip'
cd P_Control
7za a ../P_Control.zip .
cd ..

echo Renaming archive to 'P_Control.fmu'
rename P_Control.zip P_Control.fmu

:: all ok
exit /b 0
