import os
import sys
import shutil
import uuid
import time
import argparse
import FMIGenerator


#create new root folder with the name given in "New_Name"
def create_folder(adrs):
    try:
        os.mkdir(adrs)
        shutil.rmtree(adrs)
    except:
        print("Directory already exists, replacing directory")
        shutil.rmtree(adrs)
    return

# renaming of folders,files,text
def rename_folders_files(cwd, oldpath, targetdir, oldname, newname,newdescription):
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
                data = FMIGenerator.adjust_model_description(data,localtime, guid)
                               
            if file=="FMIProject.cpp":
                data = data.replace("$$GUID$$", str(guid))            
            
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

