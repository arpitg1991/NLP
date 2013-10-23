import sys
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
	file1 = open('ner_train_new.dat','w')
	inputFile.seek(0,0)
	for line in inputFile:
		if (len(line) > 1):
			tokens = line.split(" ")
			if (len(tokens) > 0 ):
				if (words[tokens[0]] < 5):
					file1.write('_RARE_' + ' ' + tokens[1])
				else:
					file1.write(line)
		else:
			file1.write(line)


			
    
