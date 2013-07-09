#!/usr/bin/python
'''
Created on May 9, 2013
Last Edited on June 19, 2013

@author: Matt
'''
import os
import fnmatch
import subprocess
from sys import platform

# Returns a list of paths to files.
# get_file_list takes a base directory and a pattern
# It will find all of the files in the base directory and subdirectories
# that match the pattern given
def get_file_list(ndir,pattern):
    filelist = []
    for root, dirs, files in os.walk(ndir):
        for filenames in fnmatch.filter(files,pattern):
            if root == ndir:
                filelist.append(root + filenames)
            else:
                filelist.append(root + "/" + filenames)
    
    return filelist


energy_file_list = get_file_list("./","*_[0-9].nist.txt")
tp_file_list = get_file_list("./","*_[0-9].tp.nist.txt")


# Sort file lists so hopefully the species match
energy_file_list.sort()
tp_file_list.sort()

for nrg,tp in zip(energy_file_list,tp_file_list):
    if (nrg.split("."))[0] == (tp.split("."))[0]:
        print("Running nist2stout on %s and %s" % (nrg,tp))
        if platform.startswith('win'):
            rcode = subprocess.call(["nist2stout.py",nrg,tp],shell = True)
        else:
            rcode = subprocess.call(["nist2stout.py",nrg,tp])
