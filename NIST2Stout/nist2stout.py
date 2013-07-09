#!/usr/bin/python
'''
Created on May 9, 2013
Last edited on June 19, 2013

@author: Matt
'''
import sys
import datetime
import fractions

# Test whether a string can be a number
def is_number(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
    
# Remove brackets and punctuation from strings
def remove_junk(string):
    newstring = string.replace('?','').replace('[','').replace(']','').replace('+x','')
    return newstring

# Convert energies to indicies
# Input list of energies to convert, list of reference energies, list of reference indices
# Returns list of indices
def energies2indices(nrg,ref_nrg,ref_dex):
    ndex = []
    for x in nrg:
        match_found = False
        for refg,refx in zip(ref_nrg,ref_dex):
            if x == refg:
                ndex.append(refx)
                match_found = True
                break
    
        if match_found == False:
            print ("PROBLEM: No energy level match found for %f" % x)
            sys.exit(2)
            
    return ndex



DEBUGMODE = False

if len(sys.argv) != 3:
    print("Problem: You must specify the energy level and the transition probability files")
    #sys.exit(99)
    energy_file_name = "ar_2.nist.txt"
    tp_file_name = "ar_2.tp.nist.txt"    
else:
    energy_file_name = str(sys.argv[1])
    tp_file_name = str(sys.argv[2])


# Generate output filenames from the inputs
path_list = energy_file_name.split('/')
base_name = (path_list[len(path_list)-1].split('.'))[0]
base_path = ""

for x in path_list:
    if x != path_list[len(path_list)-1]:
        base_path += x + "/"

#print (path_list)
#print (base_path)


energy_output_name = base_path + base_name + ".nrg"
tp_output_name = base_path + base_name + ".tp"

print ("Outputting to %s and %s\n" % (energy_output_name,tp_output_name))

# Explicitly declare variables to be filled
energy = []
configuration = []
term = []
statwt = []
J = []
old_config = ""
old_term = ""

energy_file = open(energy_file_name,"r")
for current_line in energy_file:    
    line_list = current_line.split('|')    
    tempenergy = remove_junk(line_list[3].strip())
    tempJ = remove_junk(line_list[2].strip())
    #Save the potential fractional form of J to add to the term
    saveJ = tempJ
        
    # Deal with J when it is a fraction
    # If J does not appear to be a fraction or number, go to the next line
    if is_number(tempJ) == False:
        try:
            tempJ = float(fractions.Fraction(tempJ))
        except:
            if DEBUGMODE == True:
                print ("Problem: The J between the brackets [%s] does not appear to be a number." % tempJ)
            continue            
            
    # Only process lines that have a number for the energy and J
    if is_number(tempenergy) and is_number(tempJ):        
        tempconfig = line_list[0].strip()                
        # Duplicate missing configuration and term information
        if  tempconfig == "":
            configuration.append(old_config)
        else:
            configuration.append(tempconfig)
            old_config = tempconfig        
        
        tempterm = line_list[1].strip()
        if  tempterm == "":
            term.append(old_term + saveJ)
        else:
            term.append(tempterm + saveJ)
            old_term = tempterm
            
        J.append(float(tempJ))    
        
        statwt.append(2*float(tempJ) + 1)        
        tempenergy = float(tempenergy)
        energy.append(tempenergy)

energy_file.close()

#Create index list
index = range(1,len(energy)+1)

energy_output = open(energy_output_name,"w")

#Write out the magic number at the top of the file
energy_output.write("11 10 14\n")

for ndex,nrg,stwt,cfg,trm in zip(index,energy,statwt,configuration,term):
    energy_output.write("%i\t%.3f\t%i\t%s\t%s\n" % (ndex,nrg,stwt,cfg,trm))


# Write out End of Data delimiter and NIST Reference including the current date
energy_output.write("**************\n#Reference:\n#NIST  ")
date_today = datetime.date.today()
energy_output.write(date_today.strftime("%Y-%m-%d"))

energy_output.close()
        
tp_file = open(tp_file_name,"r")
line_list = []
eina = []
nrglo = []
nrghi = []
ndexlo = []
ndexhi = []
for current_line in tp_file:
    line_list = current_line.split('|')
    temp_eina = line_list[0].strip()
    # Only process lines that have a number for the Einstein A
    if is_number(temp_eina) == True :
        eina.append(float(temp_eina))
        # Energies list item comes out of the first split containing both energies separated
        # by a "-". Split them based on "-" and strip away the whitespaces. 
        temp_nrglo = (line_list[2].split('-'))[0].strip()
        temp_nrghi = (line_list[2].split('-'))[1].strip()
        try:
            nrglo.append(float(remove_junk(temp_nrglo)))
            nrghi.append(float(remove_junk(temp_nrghi)))
        except:
            print ("PROBLEM: Cannot convert energy levels to floats in tp file")
            print ("nrglo = %s\tnrghi = %s\n" % (temp_nrglo,temp_nrghi))
            sys.exit(1)
            

tp_file.close()
#Match energy levels to indices
ndexlo = energies2indices(nrglo,energy,index)
ndexhi = energies2indices(nrghi,energy,index)

tp_output = open(tp_output_name,"w")
tp_output.write("11 10 14\n")

for x,y,z in zip(ndexlo,ndexhi,eina):
    tp_output.write("A\t%i\t%i\t%.2e\n" % (x,y,z))
    
tp_output.write("**************\n#Reference:\n#NIST  ")
tp_output.write(date_today.strftime("%Y-%m-%d"))
    
    
tp_output.close() 

sys.exit(0)
