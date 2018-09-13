import os
import sys
import shutil
import uuid
import time
import subprocess



class FMIGenerator():
    """Class that encapsulates all parameters needed to generate the FMU.
    
    Usage: create class instance, set member variables, call function generate()
    """
    
    def __init__(self):
        """ Construction, initializes member variables."""
        
        self.m_modelName = ""
        self.m_description = ""
        m_inputvar = []
        m_outputvar = []
        m_parameters = []
        
        """
        Member variables:
        
        m_modelName -- A user defined model name
        m_description -- A user defined description
        m_inputVar
        """
    
        
    def renameFoldersFiles(self, cwd, oldPath, targetDir, oldName):
        """Copies a folder from template data to the new location. Replaces the old name of directories, files 
        and script in the files with the newly user defined name (i.e.modelName).
        
        Arguments:
        
        cwd -- The absolute path to the current working directory.
        oldPath -- The relative path to the template data from cwd
        targetDir -- The absolute path to the user defined directory to be copied
        oldName -- Name of the folder to be copied
        """
        
        self.cwd = cwd
        self.oldPath = oldPath
        self.targetDir = targetDir
        self.oldName = oldName
    
        
        try:
            # Copy source folder to a new location(i.e.targetDir)
            shutil.copytree(cwd + "/" + oldPath + "/"+ oldName, targetDir)
            
        except:
            # Remove the folder, if already exist
            shutil.rmtree(targetDir)
            # Copy source folder to a new location(i.e.targetDir)
            shutil.copytree(cwd + "/" + oldPath + "/"+ oldName, targetDir)
            
        # Generate globally unique identifier
        guid = uuid.uuid1()
        
        # Generate local date and time
        localtime = time.strftime('%Y-%m-%dT%I:%M:%SZ',time.localtime())
        
        # Path to check the name of the directories, files, script in files in new folder  
        src = ""
        # Path refering the directories, files, script in files after renaming in new folder
        dst = ""
        
        
        # loop to walk through the new folder  
        for root, dircs, files in os.walk(targetDir):
            # loop to replace the old name of directories into user defined new name(i.e modelName)
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
                
        return


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
            self.renameFoldersFiles(cwd, oldPath, targetDir, oldName)
        else:
            print ("This is an original file")
            
        # calling build.sh file
        #subprocess.call('targetDir/build', -1)
        #subprocess.call('ls',-1)
        #subprocess.run(["ls","-1","/bin/deploy"],capture_output=True)

    
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
        

        data = data.replace("$$description$$", self.description)
        data = data.replace("$$modelName$$",self.modelName)    
        data = data.replace("$$dateandtime$$",time)
        data = data.replace("$$GUID$$", str(guid))
        return data 
    
    
    
    
