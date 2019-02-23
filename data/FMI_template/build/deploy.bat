@echo on

:: script is supposed to be executed in /build directory

:: remove target directory if it exists
IF EXIST %FMI_template% (
	RMDIR /S /Q "FMI_template"  
)

:: remove target FMU if it exists
IF EXIST %FMI_template.fmu% (
	DEL /F /S /Q "FMI_template.fmu"
)	
::create subdir and change into it
MKDIR FMI_template 

cd FMI_template 

:: create binary dir for Windows
MKDIR binaries/Windows

:: copy shared library, we expect it to be already renamed correctly
cp ..\..\bin\release\FMI_template.so binaries\Windows\FMI_template.so
cp ..\..\data\modelDescription.xml


::create zip archive
7z a -tzip %..\FMI_template.zip% -r %FMI_template\*.h
cd ..
move ..\FMI_template.zip ..\FMI_template.fmu
echo "Created FMI_template.fmu"

::change working directory back to original dir
cd ..