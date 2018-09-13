import os
import sys
import shutil
import uuid
import time
import subprocess



class FMIGenerator():
    
    def _init_(self):
        self.modelName = ""
        self.description = ""
        inputvar = []
        outputvar = []
        parameters = []
        
   #create new root folder with the name given in "New_Name"
        
    def create_folder(self,adrs):
        self.adrs=adrs
        try:
            os.mkdir(adrs)
            shutil.rmtree(adrs)
        except:
            print("Directory already exists, replacing directory")
            shutil.rmtree(adrs)
        return


   # renaming of folders,files,text
    def rename_folders_files(self, cwd, oldpath, targetdir, oldname):

        self.cwd = cwd
        self.oldpath = oldpath
        self.targetdir = targetdir
        self.oldname = oldname
    
        src = ""
        dst = ""   
        shutil.copytree(cwd + "/" + oldpath + "/"+ oldname, targetdir)
        print("Copying directory structure into new root directory!!!!")
         
        # generate global unique identifier ID
        guid=uuid.uuid1()
        
        # generate date and time
        localtime = time.strftime('%Y-%m-%dT%I:%M:%SZ',time.localtime())
        
        
        for root, dircs, files in os.walk(targetdir):
            for dirc in dircs:
                if oldname in dirc:
                    src = os.path.join(root,dirc)
                    dst = os.path.join(root,dirc.replace(oldname, self.modelName))
                    os.rename(src,dst)
                    print("Directory renamed as '{}'".format(dirc))
                    #else:
                        #print("no match")
                
            for file in files:
                    
                # compose full file path
                src = os.path.join(root,file)
                    
                # read file into memory, variable 'data'
                fobj=open(src,'r')
                data=fobj.read()
                fobj.close()

                # generic data adjustment
                data = data.replace(oldname,self.modelName)            
                    
                    
                # process data depending on file type
                if file == "modelDescription.xml":
                    data = self.adjust_model_description(data, localtime, guid)
                                       
                if file=="FMIProject.cpp":
                    data = data.replace("$$GUID$$", str(guid))            
                    
                #finally, write data back to file
                    
                fobj=open(src,'w')
                fobj.write(data)
                fobj.close()
                    
                if oldname in file:
                    dst = os.path.join(root,file.replace(oldname, self.modelName))
                    os.rename(src,dst)
                    print("'{}' renamed" .format(file))
                # else:
                    #print("no match")
        return


    def generate(self):
    
        # FMUIDName is interpreted as directory name
        # directory structure should be created relative to current working directory, so full
        # path to new directory is:
        
        
        targetdir = os.path.join(os.getcwd(), self.modelName)
        print("Creating directory '{}'".format(targetdir))
    
        # the source directory with the template files is located relative to
        # this python script: ../data/FMIProject
    
        # get the path of the current python script
    
        scriptpath = os.path.abspath(os.path.dirname(sys.argv[0]))
    
        oldname = "FMIProject" #Old name of files and folders
        oldpath = "../data" 
        cwd=os.getcwd()
    
        if self.modelName!=oldname:
            self.create_folder(targetdir)
            self.rename_folders_files(cwd, oldpath, targetdir, oldname)
        else:
            print ("This is an original file")
            
        # calling build.sh file
        #subprocess.call('targetdir/build', -1)
        #subprocess.call('ls',-1)
        #subprocess.run(["ls","-1","/bin/deploy"],capture_output=True)

    
    def adjust_model_description(self, data, time, guid):
        self.data = data
        self.time = time
        self.guid = guid
        data = data.replace("$$description$$", self.description)
        data = data.replace("$$modelName$$",self.modelName)    
        data = data.replace("$$dateandtime$$",time)
        data = data.replace("$$GUID$$", str(guid))
        return data 
    
    
    
    
