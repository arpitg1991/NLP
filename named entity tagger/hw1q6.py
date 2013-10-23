'''
replaces infrequent words with certain categories, 
if the infrequent words do not fit onto any category
then they are replaced by _RARE_
'''
import sys
import re
import os
if __name__ == "__main__":
	if len(sys.argv)!=2: # Expect exactly one argument: the training data file
		sys.exit(2)
	try:
			inputFile = open(sys.argv[1],"r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile %s.\n" % arg)
		sys.exit(1)
	words = dict()
	
	for line in inputFile:
		
		if (len(line) > 1 ):
			tokens = line.split(" ")
			if ( len(tokens) > 0 ):
				#print (tokens[0])
				if (tokens[0] in words):	
					words[tokens[0]] = words[tokens[0]] + 1
				else:
					words[tokens[0]] = 1
	#file1 = open('RareWords.dat','w')

	#Regular Expression for numbers with or without symbols
	num = re.compile('^[\.\-\+]*[0-9]+[0-9\.\-\+:,]*$') 
	#Regular Expression for All Caps that are 2 or more characters long
	allCaps = re.compile('^[A-Z][A-Z]+$')
	#Regex for (AlPhabeT-)*
	capsDash = re.compile('^([A-Za-z]+(-)+)|((-)+[A-Za-z]+)[A-Za-z-]+$')
	#Regex for AlphaNummeric words with or without symbols
	alphaNum = re.compile('^[\.\-\+]*(([A-Za-z]+[0-9]+)|([0-9]+[A-Za-z]+))[A-Za-z0-9\.\-\+:,]*$')
	#Regex for abbreviations of the form m.p.h or U.N.
	abv = re.compile('^([A-Za-z]\.)+$')
	#Regex for Proper nouns-> have first letter capital, we can use this because we are only categorising words
	#with count < 5 , so common words like 'The', that appear at the start of sentence will not be counted
	pn = re.compile('^[A-Z][a-z]+$')
	file1 = open('ner_train_regex.dat','w')
	
	count0 = 0
	count1 = 0  
	count2 = 0 
	count3 = 0 
	count4 = 0 
	count5 = 0
	count6 = 0
	inputFile.seek(0,0)
	
	for line in inputFile:
		if (len(line) > 1):
			tokens = line.split(" ")
			if (len(tokens) > 0 ):
				if (words[tokens[0]] < 5):
					m1 = num.search(tokens[0])
					m2 = allCaps.search(tokens[0])
					m3 = capsDash.search(tokens[0])
					m4 = alphaNum.search(tokens[0])
					m5 = abv.search(tokens[0])
					m6 = pn.search(tokens[0])

					if m1:
						file1.write('_NUM_' + ' ' + tokens[1])
						count1 = count1 + 1
					elif m5:
						file1.write('_ABV_' + ' ' + tokens[1])
						count5 = count1 + 1
					elif m3:
						file1.write('_CAPS-DASH_' + ' ' + tokens[1])
						count3 = count1 + 1
					elif m6:
						file1.write('_PN_' + ' ' + tokens[1])
						count6 = count6 + 1
					elif m4:
						file1.write('_ALPHANUM_' + ' ' + tokens[1])
						count4 = count1 + 1
					elif m2:
						file1.write('_CAPS_' + ' ' + tokens[1])
						count2 = count1 + 1
					else:
						file1.write('_RARE_' + ' ' + tokens[1])
						count0 = count0 + 1
				else:
					file1.write(line)


				
		else:
			file1.write(line)

	print('No of infrequent words which are all caps = ' + str(count2))
	print('No of infrequent words which are numbers with or without symbols = ' + str(count1))
	print('No of infrequent words which are Alpha Numeric = ' + str(count4))
	print('No of infrequent words which are Abbreviations = ' + str(count5))
	print('No of infrequent words which are Capitals with hypens = ' + str(count3))
	print('No of infrequent words which have first letter capital = ' + str(count6))
	print('No of infrequent words which do not fall in any category = ' + str(count0))
	