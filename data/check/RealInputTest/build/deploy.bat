@echo off
:: script is supposed to be executed in /build directory

if exist ..\bin\release_x64\RealInputTest.dll goto DLL_EXISTS
echo "ERROR: File RealInputTest.dll expected in directory ..\bin\release_x64\RealInputTest.dll, but does not exist.
exit /b 1
:DLL_EXISTS

:: remove target directory if it exists
if not exist RealInputTest goto DIRECTORY_CLEAN
echo Removing existing directory 'RealInputTest'
rd /S /Q "RealInputTest"
:DIRECTORY_CLEAN

:: remove target FMU if it exists
if not exist RealInputTest.fmu goto FMU_REMOVED
echo Removing existing FMU file 'RealInputTest.fmu'
del /F /S /Q "RealInputTest.fmu"
:FMU_REMOVED

::create subdir and change into it
mkdir RealInputTest

cd RealInputTest

:: create binary dir for Windows
mkdir binaries\win64

:: copy shared library, we expect it to be already renamed correctly
xcopy ..\..\bin\release_x64\RealInputTest.dll binaries\win64\
xcopy ..\..\data\modelDescription.xml .
echo Created FMU directory structure

::change working directory back to original dir
cd ..

::create zip archive
echo Creating archive 'RealInputTest.zip'
cd RealInputTest
7za a ../RealInputTest.zip .
cd ..

echo Renaming archive to 'RealInputTest.fmu'
rename RealInputTest.zip RealInputTest.fmu

:: all ok
exit /b 0
