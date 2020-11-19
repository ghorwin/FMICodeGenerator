@echo off
:: script is supposed to be executed in /build directory

if exist ..\bin\release_x64\Test5.dll goto DLL_EXISTS
echo "ERROR: File Test5.dll expected in directory ..\bin\release_x64\Test5.dll, but does not exist.
exit /b 1
:DLL_EXISTS

:: remove target directory if it exists
if not exist Test5 goto DIRECTORY_CLEAN
echo Removing existing directory 'Test5'
rd /S /Q "Test5"
:DIRECTORY_CLEAN

:: remove target FMU if it exists
if not exist Test5.fmu goto FMU_REMOVED
echo Removing existing FMU file 'Test5.fmu'
del /F /S /Q "Test5.fmu"
:FMU_REMOVED

::create subdir and change into it
mkdir Test5

cd Test5

:: create binary dir for Windows
mkdir binaries\win64

:: copy shared library, we expect it to be already renamed correctly
xcopy ..\..\bin\release_x64\Test5.dll binaries\win64\
xcopy ..\..\data\modelDescription.xml .
echo Created FMU directory structure

::change working directory back to original dir
cd ..

::create zip archive
echo Creating archive 'Test5.zip'
cd Test5
7za a ../Test5.zip .
cd ..

echo Renaming archive to 'Test5.fmu'
rename Test5.zip Test5.fmu

:: all ok
exit /b 0
