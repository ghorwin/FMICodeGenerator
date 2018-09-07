import os
import sys
import shutil
import uuid


#create new root folder with the name given in "New_Name"
def create_folder(adrs):
    try:
        os.mkdir(adrs)
        shutil.rmtree(adrs)
    except:
        print("Directory already exists, replacing directory")
        shutil.rmtree(adrs)
    return

def rename_folders_files(cwd, oldpath, targetdir, oldname, newname):
    src = ""
    dst = ""
    shutil.copytree(cwd + "/" + oldpath + "/"+ oldname, targetdir)
    print("Copying directory structure into new root directory!!!!")
    
    # generate global unique identifier ID
    guid=uuid.uuid1()
    
        
    for root, dircs, files in os.walk(targetdir):
        for dirc in dircs:
            if oldname in dirc:
                src = os.path.join(root,dirc)
                dst = os.path.join(root,dirc.replace(oldname, newname))
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
            data = data.replace(oldname,newname)            
            
            # process data depending on file type
            if file == "modelDescription.xml":
                guidstr="$$GUID$$"
                data = data.replace(guidstr, str(guid))                
            if file=="FMIProject.cpp":
                guidstr="$$GUID$$"
                data = data.replace(guidstr, str(guid))            
            
            #finally, write data back to file
            
            fobj=open(src,'w')
            fobj.write(data)
            fobj.close()
            
            if oldname in file:
                dst = os.path.join(root,file.replace(oldname, newname))
                os.rename(src,dst)
                print("'{}' renamed" .format(file))
           # else:
                #print("no match")
    return

def generateFMU(FMUIDName):

    # FMUIDName is interpreted as directory name
    # directory structure should be created relative to current working directory, so full
    # path to new directory is:
    
    targetdir = os.path.join(os.getcwd(), FMUIDName)
    print("Creating directory '{}'".format(targetdir))

    # the source directory with the template files is located relative to
    # this python script: ../data/FMIProject
    
    # get the path of the current python script
    
    scriptpath = os.path.abspath(os.path.dirname(sys.argv[0]))
    print scriptpath
    
    oldname = "FMIProject" #Old name of files and folders
    oldpath = "../data" 
    cwd=os.getcwd()
    
    if FMUIDName!=oldname:
        newname = FMUIDName     #Update the name of files and folder
        create_folder(targetdir)
        rename_folders_files(cwd, oldpath, targetdir, oldname, newname)
    else:
        print ("This is an original file")
#def GUID():
    #seed = random.getrandsbits(32)
    #while True:
        #yield seed
        #see+=1

#unique=GUID()

#print unique

       