'''
I create a separate dictionary to store weights of features, whenever there is a cnage in the feature. 
Later on after all iterations , t*n , weights are updated by averaging as described in assignment
'''
from collections import defaultdict as dd
from subprocess import PIPE
import sys, subprocess,sets
V = dict()

sentenceList = []
sentenceTagList = []
def readFeatures(featureFile):
	for line in featureFile:
		line = line.strip()
		tokens = line.split(' ')
		score = float(tokens[1])
		tokens = tokens[0].split(':')
		V[(tokens[0],tokens[1],tokens[2])] = score

def process(args):
  "Create a 'server' to send commands to."
  return subprocess.Popen(args, stdin=PIPE, stdout=PIPE)

def call(process, stdin):
  "Send command to a server and get stdout."
  output = process.stdin.write(stdin + "\n\n")
  line = ""
  while 1: 
    l = process.stdout.readline()
    if not l.strip(): break
    line += l
  return line

# Create a history server.
gold_server = process(
  ["python", "tagger_history_generator.py",  "GOLD"])
enum_server = process(
	["python","tagger_history_generator.py","ENUM"])
decoder_server = process(
	["python", "tagger_decoder.py","HISTORY"])

'''
Description of Dictionaries for storing weights
'''
featuresGlobal = dd(int)   #stores runnning weights as in previous problems


featuresAvg = dd(lambda: [])  # stores weights whenever they change, along with information about at which iteration the weight changed for that particular feature


featuresFinal = dict()  ### stores final averaged Weights


def readTrainFile(trainFile):

	totalLines = len(trainFile)
	ctr = 0
	while ctr < totalLines:
		sentence = []
		tagList = []
		readMore = True
		splitLine = trainFile[ctr].split('\t')
		sentence.append(splitLine[0])
		tagList.append(splitLine[1])
		ctr = ctr  + 1
		while(readMore and ctr < totalLines ):
			line = trainFile[ctr]
			ctr += 1 
			lineStrip = line.strip()
				
			if (lineStrip):
				line = line.split('\t')
				sentence.append(line[0])
				tagList.append(line[1])
			else:
				readMore = False
				sentence[len(sentence) - 1] = sentence[len(sentence) - 1 ].strip()
		sentenceList.append(sentence)
		sentenceTagList.append(tagList)
		
	totalSentences = len(sentenceList)
	
	iterBig = 0
	for iterations in range(0,5):
		
		
		sanity = 0
		for ctr in range(0,totalSentences):
			iterBig += 1 
			sent = '\n'.join(sentenceList[ctr])
			
			enum_history = call(enum_server,sent)
			enum_history = enum_history.splitlines()
			features = dict()
			tagsSet = set()
			for history in enum_history:
				history = history.split()
				features[(str(history[0]),history[1],history[2])] = featuresGlobal[('BIGRAM',history[1],history[2])]
				features[(str(history[0]),history[1],history[2])] += featuresGlobal[('TAG',sentenceList[ctr][int(history[0]) - 1],history[2])]
				for i in range(-1,-(min(len(sentenceList[ctr][int(history[0]) - 1]),3))-1,-1):
					suffix = sentenceList[ctr][int(history[0]) - 1][i:]
					features[(str(history[0]),history[1],history[2])] += featuresGlobal[('SUFFIX',suffix,history[2])]
			featureList = []
			for history in enum_history:
				history = history.split()
				unrollFeature = ' '.join(history)
				unrollFeature = unrollFeature + ' ' + str(features[(history[0],history[1],history[2])])
				featureList.append(unrollFeature)	
			finalFeatureList = '\n'.join(featureList)
			
			tagSequence = call(decoder_server,finalFeatureList)
			tagSequence = tagSequence.strip()
			tagSequence = tagSequence.split('\n')
			tagSequenceFinal = []
			firstTag = tagSequence[0].split()[1]
			for i in range(0,len(sentenceList[ctr])):
				tags = tagSequence[i].split()
				tagSequenceFinal.append(tags[2])
			needToUpdate = False
			for i in range(0,len(sentenceList[ctr])):
				if (tagSequenceFinal[i] != sentenceTagList[ctr][i]):
					needToUpdate = True
					break
			if (needToUpdate):
				sanity += 1 
				for i in range(0,len(sentenceList[ctr])):
					featuresGlobal[('TAG',sentenceList[ctr][i],tagSequenceFinal[i])] -=  1.0
					featuresGlobal[('TAG',sentenceList[ctr][i],sentenceTagList[ctr][i])] += 1.0
					featuresAvg[('TAG',sentenceList[ctr][i],tagSequenceFinal[i])].append((iterBig,featuresGlobal[('TAG',sentenceList[ctr][i],tagSequenceFinal[i])]))
					featuresAvg[('TAG',sentenceList[ctr][i],sentenceTagList[ctr][i])].append((iterBig,featuresGlobal[('TAG',sentenceList[ctr][i],sentenceTagList[ctr][i])]))
					for L in range(-1,-(min(len(sentenceList[ctr][i]),3))-1,-1):
						suffix = sentenceList[ctr][i][L:]
						featuresGlobal[('SUFFIX',suffix,tagSequenceFinal[i])] -= 1.0
						featuresGlobal[('SUFFIX',suffix,sentenceTagList[ctr][i])] += 1.0
						featuresAvg[('SUFFIX',suffix,tagSequenceFinal[i])].append((iterBig,featuresGlobal[('SUFFIX',suffix,tagSequenceFinal[i])]))
						featuresAvg[('SUFFIX',suffix,sentenceTagList[ctr][i])].append((iterBig,featuresGlobal[('SUFFIX',suffix,sentenceTagList[ctr][i])]))
						
					if ( i == 0):
						featuresGlobal[('BIGRAM','*',tagSequenceFinal[i])] -=  1.0
						featuresGlobal[('BIGRAM','*',sentenceTagList[ctr][i])] +=  1.0
						featuresAvg[('BIGRAM','*',tagSequenceFinal[i])].append((iterBig,featuresGlobal[('BIGRAM','*',tagSequenceFinal[i])]))
						featuresAvg[('BIGRAM','*',sentenceTagList[ctr][i])].append((iterBig,featuresGlobal[('BIGRAM','*',sentenceTagList[ctr][i])]))
					else:
						featuresGlobal[('BIGRAM',tagSequenceFinal[i-1],tagSequenceFinal[i])] -=  1.0
						featuresGlobal[('BIGRAM',sentenceTagList[ctr][i-1],sentenceTagList[ctr][i])] +=  1.0
						featuresAvg[('BIGRAM',tagSequenceFinal[i-1],tagSequenceFinal[i])].append((iterBig,featuresGlobal[('BIGRAM',tagSequenceFinal[i-1],tagSequenceFinal[i])]))
						featuresAvg[('BIGRAM',sentenceTagList[ctr][i-1],sentenceTagList[ctr][i])].append((iterBig,featuresGlobal[('BIGRAM',sentenceTagList[ctr][i-1],sentenceTagList[ctr][i])]))
			
	for key in featuresAvg:
		valSum = 0
		for ii in range(0,len(featuresAvg[key])):
			if (ii < len(featuresAvg[key])-1 ):
				valSum += float((featuresAvg[key][ii+1][0] - featuresAvg[key][ii][0])*featuresAvg[key][ii][1])
			else:
				valSum += float((iterBig - featuresAvg[key][ii][0])*featuresAvg[key][ii][1])
		valSum = float(valSum)/iterBig
		featuresFinal[key] = valSum


	for key in featuresFinal:
		val = key
		if featuresFinal[key] != 0:
			print (val[0] + ':' + val[1] + ':' + val[2] + ' ' + str(featuresFinal[key]))
	
if __name__ == '__main__':
	trainFile = open('tag_train.dat','r')
	featureFile = open('suffix_tagger.model','r')
	
	readTrainFile(trainFile.read().splitlines())
	