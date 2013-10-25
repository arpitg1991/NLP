import sys, json
import math

unaryRight_dict = dict()  ## dictionary of unary rules , keyed in right hand side values, i.e. terminals and values = their counts

def create_dict(inputFile):
	for line in inputFile:
		line = line.strip()
		line = line.split(" ")
		if line[1] == 'UNARYRULE':
			if line[3] in unaryRight_dict:
				unaryRight_dict[line[3]] = int(unaryRight_dict[line[3]]) + int(line[0])
			else:
				unaryRight_dict[line[3]] = int(line[0])

def replaceRare(t):           #read tree structure recursively and replace when leaf is reached, if termianl as count < 5 
	if len(t) == 2:
		if (int(unaryRight_dict[t[1]]) < 5):
			t[1] = '_RARE_'
	else:
		replaceRare(t[1])
		replaceRare(t[2])


def readWriteJSON(trainFile,filename):
	file1 = open(filename,'w')
	for line in trainFile:
		t = json.loads(line)
		replaceRare(t)
		json.dump(t,file1)
		file1.write('\n')
	file1.close()


if __name__ == "__main__": 
  if len(sys.argv) != 4:
    sys.exit(1)
  try :
  	trainFile = open(sys.argv[2],'r')
  	countFile = open(sys.argv[1],'r')
  	create_dict(countFile)
  	
  	readWriteJSON(trainFile,sys.argv[3])
  except:
  	print ( 'First input should be cfg.counts , second should be parse_train.dat, third must be output filename like rareTrain.dat') 