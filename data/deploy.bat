@echo on
pause
:: script is supposed to be executed in /build directory
:: current working directory
SET m = %~dp0FMI_template
echo m

:: remove target directory if it exists
@RD /S /Q "FMI_template"  

:: remove target FMU if it exists
DEL /F /S /Q "FMI_template.fmu"
	
::create subdir and change into it
MKDIR FMI_template 

cd FMI_template 

:: create binary dir for Windows
MKDIR binaries\Windows64

:: copy shared library, we expect it to be already renamed correctly
xcopy ..\..\bin\release\FMI_template.so binaries\Windows64\FMI_template.so
xcopy ..\..\data\modelDescription.xml
cd..


::create zip archive
for /d %%X in (*) do "c:\Program Files\7-Zip\7z.exe" a -mx "%%X.zip" "%%X\*"


ren "FMI_template.zip" "FMI_template.fmu.zip"
echo "Created FMI_template.fmu"

::change working directory back to original dir
cd..
