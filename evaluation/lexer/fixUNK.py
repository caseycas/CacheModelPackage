import os
from folderManager import Folder

inputFolder = Folder("/Users/caseycas/CodeNLP/EnglishSample/all/")
fileList = inputFolder.fullFileNames("*.tokens", recursive=True)

for path in fileList:
	fileContents = ''.join(open(path, 'r').readlines())
	fileContents = fileContents.replace("<UNK>", "UNK")
	with open(path, 'w') as f:
		f.write(fileContents4)