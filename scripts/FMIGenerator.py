import os
import sys
import shutil
import uuid
import time
from generate import create_folder
from generate import rename_folders_files


class FMIGenerator():
	
	def _init_(self):
		self.modelName = ""
		self.description = ""

	def generate(self):
	
		# FMUIDName is interpreted as directory name
		# directory structure should be created relative to current working directory, so full
		# path to new directory is:
		modelName = self.modelName
		description = self.description
		targetdir = os.path.join(os.getcwd(), modelName)
		print("Creating directory '{}'".format(targetdir))
	
		# the source directory with the template files is located relative to
		# this python script: ../data/FMIProject
	
		# get the path of the current python script
	
		scriptpath = os.path.abspath(os.path.dirname(sys.argv[0]))
	
		oldname = "FMIProject" #Old name of files and folders
		oldpath = "../data" 
		cwd=os.getcwd()
	
		if modelName!=oldname:
			newname = modelName     #Update the name of files and folder
			newdescription = description
			create_folder(targetdir)
			rename_folders_files(cwd, oldpath, targetdir, oldname, newname, newdescription)
		else:
			print ("This is an original file")
		# calling build.sh file
	
		#os.system('sh'+ 'newname/build/build.sh')

	
	def adjust_model_description(self, description, modelName, data, time, guid):
		self.data = data
		self.time = time
		self.guid = guid
		data = data.replace("$$description$$", description)
		data = data.replace("$$modelName$$",modelName)    
		data = data.replace("$$dateandtime$$",time)
		data = data.replace("$$GUID$$", str(guid))
		return data	
	
	
	
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
	