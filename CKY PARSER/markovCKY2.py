import sys
import os,json
import math
from collections import defaultdict as dd

binaryRight = dict()
binaryLeft = dict()
unaryRight = dict()
nonTerminal = dict()
negInf = float(-sys.maxint)
pi = dd(lambda: dd(lambda: dd(lambda: negInf)))
bp = dd(lambda: dd(lambda: dd(lambda: 'NONE')))
rules = dict()   # key values are of the form (i,j) ( span of rule) ; value is a tuple of the form (X, Y, Z, s) or (X, Y) 

def create_dict(inputFile):
	for line in inputFile:
		line = line.strip()
		line = line.split(" ")
		if line[1] == 'UNARYRULE':
			if line[3] in unaryRight:
					unaryRight[line[3]][line[2]] = line[0]
			else:
				unaryRight[line[3]] = dict()
				unaryRight[line[3]][line[2]] = line[0]
		elif line[1] == 'BINARYRULE':
			if (line[3],line[4]) in binaryRight:
				binaryRight[(line[3],line[4])][line[2]] = line[0]
			else:
				binaryRight[(line[3],line[4])] = dict()
				binaryRight[(line[3],line[4])][line[2]] = line[0]
			if line[2] in binaryLeft:
				binaryLeft[line[2]][(line[3],line[4])] = line[0]
			else:
				binaryLeft[line[2]] = dict()
				binaryLeft[line[2]][(line[3],line[4])] = line[0]
		elif line[1] == 'NONTERMINAL':
			nonTerminal[line[2]] = line[0]
		else:
			#sanity check
			print ( 'There is a fourth type of object in counts File, check crete_dict func')

def binaryRuleEstimate(X,Y,Z):
	countRight = 0 ; 
	countLeft = 0;
	if (Y,Z) in binaryRight:
		if X in binaryRight[(Y,Z)]:
			countRight = binaryRight[(Y,Z)][X]
	if X in nonTerminal:
		countLeft = nonTerminal[X]
	if (countRight == 0 ):
		return negInf
	else:
		return math.log(float(countRight),2) - math.log(float(countLeft),2)

def unaryRuleEstimate(X,Y):
	countRight = 0 ; 
	countLeft = 0;
	if Y in unaryRight:
		if X in unaryRight[Y]:
			countRight = unaryRight[Y][X]
	if X in nonTerminal:
		countLeft = nonTerminal[X]
	if (countRight == 0 ):
		return negInf
	else:
		return math.log(float(countRight),2) - math.log(float(countLeft),2) #log values so subtracting instead of dividing

def getRules(root,sentence):  # root tuple is i j X
	children = bp[root[0]][root[1]][root[2]]  # X Y Z s is in children tuple
	#print(root,children)
	rules[(root[0],root[1])] = children
	#if either of the child extracted is at last but one level i.e. s-i == 1 or j-s == 1, add leaf node rule as well

	#left child
	leftTuple = (root[0],children[3],children[1]) 
	
	if (int(leftTuple[1]) - int(leftTuple[0]) == 0):
		
		rules[(leftTuple[0],leftTuple[0])] = (children[1],sentence[leftTuple[0] - 1]) 
	else:
		#print(leftTuple)
		getRules(leftTuple,sentence)

	#right child 
	rightTuple = (children[3]+1,root[1],children[2]) ;
	if (int(rightTuple[1]) - int(rightTuple[0]) == 0):
		rules[(rightTuple[0],rightTuple[0])] = (children[2],sentence[rightTuple[0] - 1]) 
	else:
		getRules(rightTuple,sentence)

def create_tree_structure(begin,end): #begin end both included
	node = []
	rule = rules[(begin,end)]  # X Y Z s 
	if len(rule) == 4:
		head = rule[0]
		left = create_tree_structure(begin,rule[3])
		right = create_tree_structure(rule[3]+1,end)
		node.append(head)
		node.append(left)
		node.append(right)
	elif len(rule) == 2:
		node.append(rule[0])
		node.append(rule[1])
	else:
		print ('something wrong must be happening in rules dict')
	return node


	
	
def cky(sentence):
	#pi = dd(lambda: dd(lambda: dd(lambda: negInf)))
	#bp = dd(lambda: dd(lambda: dd(lambda: 'NONE')))
	i = 0
	n = len(sentence)
	for word in sentence:
		i = i + 1
		if word in unaryRight:
			for X in unaryRight[word]:
				pi[i][i][X] = unaryRuleEstimate(X,word)
				
		else:
			 for X in unaryRight['_RARE_']:
				pi[i][i][X] = unaryRuleEstimate(X,'_RARE_')

	for l in range(1,n):
		for i in range(1,n-l+1):
			j = i+l
			
			for s in range(i,j):
				for Y in pi[i][s]:
					for Z in pi[s+1][j]:
						if (Y,Z) in binaryRight:
							for X in binaryRight[(Y,Z)]:
								curVal = binaryRuleEstimate(X,Y,Z) + float(pi[i][s][Y]) + float(pi[s+1][j][Z]) #log values so adding instead of multiplying
								if X in pi[i][j]:
									if pi[i][j][X] < curVal:
										pi[i][j][X] = curVal;
										bp[i][j][X] = (X,Y,Z,s)
								else:
									pi[i][j][X] = curVal;
									bp[i][j][X] = (X,Y,Z,s)

	'''
	Get the rules by using backpointers 
	'''
	rules = []
	#print len(bp[1][n])
	# if pi[1][n][S] exists then take S, otherwise search over maximum 
	if 'S' in pi[1][n]:
		#print('Hello')
		#print('len ' + str(n))
		#print(bp[1][n]['S'])
		getRules((1,n,'S'),sentence)
	else:
		max1 = negInf
		maxnt = 'none'
		for nt in bp[1][n]:
			#print (nt)
			if pi[1][n][nt] > max1:
				max1 = pi[1][n][nt]
				maxnt = nt
		getRules((1,n,nt),sentence)
	
	return create_tree_structure(1,n)

def runCKY(inputFile,outputFile):
	outFile = open(outputFile,'w')
	for sentence in inputFile:
		sentence = sentence.strip()
		sentence = sentence.split(" ")
		tree = cky(sentence)
		json.dump(tree,outFile)
		bp.clear()
		pi.clear()
		rules.clear()
		outFile.write('\n')

	outFile.close()
	
if __name__ == '__main__':
	if len(sys.argv) != 4:
	    print ( '1First input should be rarecfg.counts , second should be parse_dev.dat, third should name of result File') 

	    sys.exit(1)
	
  	sentenceFile = open(sys.argv[2],'r')
  	countFile = open(sys.argv[1],'r')
  	create_dict(countFile)
  	outputFile = sys.argv[3]
  	runCKY(sentenceFile,outputFile)
	  	
	#except:
	#	print ( 'First input should be rarecfg.counts and second should be parse_dev.dat') 
