import os
import sys
import shutil
from shutil import *
import uuid
import time
import subprocess
import datetime
import platform
from third_party.send2trash_master.send2trash import send2trash


class FMIGenerator():
    """Class that encapsulates all parameters needed to generate the FMU.
    
    Usage: create class instance, set member variables, call function generate()
    """
    
    def __init__(self):
        """ Construction, initializes member variables."""
        
        self.modelName = ""
        self.description = ""
        self.inputvar = []
        self.outputvar = []
        self.parameters = []
        
        """
        Member variables:
        
        m_modelName -- A user defined model name
        m_description -- A user defined description
        m_inputVar
        """
    
        
    def copyFolderFiles(self, scriptpath, oldPath, targetDir, oldName):
        """Copies a folder from template data to the new location. Replaces the old name of directories, files 
        and script in the files with the newly user defined name (i.e.modelName).
        
        const-function.
        
        Arguments:
        
        scriptpath -- The absolute path to the script.
        oldPath -- The relative path to the template data from scriptpath
        targetDir -- The absolute path to the user defined directory to be copied
        oldName -- Name of the folder to be copied
        """
        
                   
        try:
            # Check if the folder already exist with the same name
            if self.modelName!=-1:
                send2trash(self.modelName)
                # Moves the folder to thrash
                compat(self.modelName)
                # Copy source folder to a new location(i.e.targetDir)
                shutil.copytree(scriptpath + "/" + oldPath + "/"+ oldName, targetDir)
                # Generates modified time
                os.utime(targetDir,None)

        except:
            # Copy source folder to a new location(i.e.targetDir)           
            shutil.copytree(scriptpath + "/" + oldPath + "/"+ oldName, targetDir)
            # Generates modified time
            os.utime(targetDir,None)
       
    def rename(self, targetDir, oldName):  
        """1. It generates globally unique identifier
           2. It generates local time
           3. It renames all the folder,files and script from oldName with the modelName.
           
        Arguments:  
           
           targetDir -- The absolute path to the user defined directory to be copied
           oldName -- Name of the folder to be copied
        """
        
        # Generate globally unique identifier
        guid = uuid.uuid1()
        
        # Generate local date and time
        localtime = time.strftime('%Y-%m-%dT%I:%M:%SZ',time.localtime())
        
        # Path to check the name of the directories, files, script in files in new folder  
        src = ""
        # Path refering the directories, files, script in files after renaming in new folder
        dst = ""
        
        
        # loop to walk through the new folder  
        for root, dircs, files in os.walk(targetDir,oldName):
            # loop to replace the old name of directories into user defined new name(i.e modelName)
            os.utime(root,None)
            for dirc in dircs:
                if oldName in dirc:
                    # compose full path of old named directory inside the new folder
                    src = os.path.join(root,dirc)
                    # compose full path of newly named directory inside new folder
                    dst = os.path.join(root,dirc.replace(oldName, self.modelName))
                    os.rename(src,dst)
                    
    
            # loop to replace the old name of files and in script into a new name (i.e.modelName)  
            for file in files:
                    
                # compose full file path
                src = os.path.join(root,file)
                    
                # read file into memory, variable 'data'
                fobj = open(src,'r')
                data = fobj.read()
                fobj.close()

                # generic data adjustment
                data = data.replace(oldName,self.modelName)            
                    
                    
                # process data depending on file type
                if file == "modelDescription.xml":
                    data = self.adjustModelDescription(data, localtime, guid)
                                       
                if file=="FMIProject.cpp":
                    data = data.replace("$$GUID$$", str(guid))            
                    
                #finally, write data back to file
                    
                fobj=open(src,'w')
                fobj.write(data)
                fobj.close()
                    
                if oldName in file:
                    dst = os.path.join(root,file.replace(oldName, self.modelName))
                    os.rename(src,dst)
                    print("'{}' renamed" .format(file))
                
    
    def generate(self):
        
        """ Function which is executed from main.py through class FMIGenerator()
        
        Usage: 
            1. It calls defined function 'renameFolderFile()', to replace the old name with the 
            new name (i.e. modelName) in directories,files, scripts. 
            2. It calls defined function 'adjustModelDescription()', to replace modelName, description, 
            date and time, and GUID
        """
    
        # FMUIDName is interpreted as directory name
        # directory structure should be created relative to current working directory, so full
        # path to new directory is:
        
        targetDir = os.path.join(os.getcwd(), self.modelName)
        print("Creating directory '{}'".format(targetDir))
        
        # the source directory with the template files is located relative to
        # this python script: ../data/FMIProject
    
        # get the path of the current python script
        scriptpath = os.path.abspath(os.path.dirname(sys.argv[0]))
        
        #Old name of files and folders
        oldName = "FMI_template" 
        
        #Old path or source path of template data
        oldPath = "../data" 
        
        # The absolute path to the current working directory
        cwd=os.getcwd()
    
        if self.modelName!=oldName:
            self.copyFolderFiles(scriptpath, oldPath, targetDir, oldName)
            self.rename(targetDir,oldName)
        
            
        #calling build.sh file
        # generate path to /bin subdir
        bindir = targetDir + "/build"
        
        try:
            # Check for the platform on which the shell script will execute
            # Shell file execution for Windows
            
            if platform.system() == "Windows":
                # start the external shell script to build the FMI library
                pipe = subprocess.Popen(["bash", './build.sh'], cwd = bindir, stdout = subprocess.PIPE, stderr = subprocess.PIPE)                
                # retrieve output and error messages
                outputMsg,errorMsg = pipe.communicate()  
                # get return code
                rc = pipe.returncode 
		
                # if return code is different from 0, print the error message
                if rc != 0:
                    print "Error during compilation of FMU"
                    print errorMsg
                    return
                else:
                    print "Compiled FMU successfully"
		    
		# renaming file    
		binDir = targetDir + "/bin/release"
		for root, dircs, files in os.walk(binDir):
		    for file in files:
			if file == 'lib'+ self.modelName + '.so.1.0.0':
			    oldFileName = os.path.join(binDir,'lib'+ self.modelName + '.so.1.0.0')
			    newFileName = os.path.join(binDir,'test001.dll')
			    os.rename(oldFileName,newFileName)

		
		deploy = subprocess.Popen(["bash", './deploy.sh'], cwd = bindir, stdout = subprocess.PIPE, stderr = subprocess.PIPE)                           
		outputMsg,errorMsg = deploy.communicate()  
		dc = deploy.returncode             
	    
		if dc != 0:
		    print "Error during compilation of FMU"
		    print errorMsg
		    return
		else:                    
		    print "Compiled FMU successfully"	                 
	     
            else:
                # shell file execution for Mac & Linux
                pipe = subprocess.Popen(["bash", './build.sh'], cwd = bindir, stdout = subprocess.PIPE, stderr = subprocess.PIPE)                           
                outputMsg,errorMsg = pipe.communicate()  
                rc = pipe.returncode             
                
                if rc != 0:
                    print "Error during compilation of FMU"
                    print errorMsg
                    return
                else:                    
                    print "Compiled FMU successfully"
		
		binDir = targetDir + "/bin/release"
		for root, dircs, files in os.walk(binDir):
		    for file in files:
			if file == 'lib'+ self.modelName + '.so.1.0.0':
 			    oldFileName = os.path.join(binDir,'lib'+ self.modelName + '.so.1.0.0')
			    # chnage of file extension depending on type of platform
			    if platform.system() == 'Darwin':
			        newFileName = os.path.join(binDir,'test001.dylib')
			    else:
				newFileName = os.path.join(binDir,'test001.so')
			    os.rename(oldFileName,newFileName)

		# shell file execution for Mac & Linux
		deploy = subprocess.Popen(["bash", './deploy.sh'], cwd = bindir, stdout = subprocess.PIPE, stderr = subprocess.PIPE)                           
		outputMsg,errorMsg = deploy.communicate()  
		dc = deploy.returncode             
	    
		if dc != 0:
		    print "Error during compilation of FMU"
		    print errorMsg
		    return
		else:                    
		    print "Compiled FMU successfully"	
            
        except OSError as e:
            print "Error executing 'bash' command line interpreter."
            return
        
        
        
   
    def adjustModelDescription(self, data, time, guid):
        """ defined function to to replace modelName, description, date and time, and GUID in file script 
        and returns the modified memory, variable 'data'.
        
        Arguments:
        
        data -- read file into memory
        time -- generated localtime(format:2018-09-13T11:59:46Z)
        guid -- globally unique identifier
        """
        self.data = data
        self.time = time
        self.guid = guid
        
        data = data.replace("$$dateandtime$$",time)
        data = data.replace("$$GUID$$", str(guid))        
        data = data.replace("$$description$$", self.description)
        data = data.replace("$$modelName$$",self.modelName)    
        
        return data 
    
    
    
    
