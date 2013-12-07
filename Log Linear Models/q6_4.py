from collections import defaultdict as dd
from subprocess import PIPE
import sys, subprocess,sets
#V = dict()

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

featuresGlobal = dd(int)
		
def readTrainFile(trainFile):

	totalLines = len(trainFile)
	ctr = 0
	while ctr < totalLines:
		sentence = []
		tagList = []
		readMore = True
		splitLine = trainFile[ctr].split('\t')
		#print splitLine
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
	
	for iterations in range(0,5):
		sanity = 0
		for ctr in range(0,totalSentences):
			sent = '\n'.join(sentenceList[ctr])
			enum_history = call(enum_server,sent)
			enum_history = enum_history.splitlines()
			features = dict()
			tagsSet = set()
			for history in enum_history:
				history = history.split()
				features[(str(history[0]),history[1],history[2])] = featuresGlobal[('BIGRAM',history[1],history[2])]
				features[(str(history[0]),history[1],history[2])] += featuresGlobal[('TAG',sentenceList[ctr][int(history[0]) - 1],history[2])]
				for i in range(-2,-(min(len(sentenceList[ctr][int(history[0]) - 1]),4))-1,-1):
					suffix = sentenceList[ctr][int(history[0]) - 1][i:]
					features[(str(history[0]),history[1],history[2])] += featuresGlobal[('SUFFIX',suffix,history[2])]
				wordIndex = int(history[0]) - 1
				if (wordIndex > 0 ):
					features[(str(history[0]),history[1],history[2])] += featuresGlobal[('TAG-WORD-1',sentenceList[ctr][wordIndex -1 ],history[2])]
				else:
					features[(str(history[0]),history[1],history[2])] += featuresGlobal[('TAG-WORD-1','*',history[2])]
				if (wordIndex < len(sentenceList[ctr]) - 1):
					features[(str(history[0]),history[1],history[2])] += featuresGlobal[('TAG-WORD+1',sentenceList[ctr][wordIndex +1 ],history[2])]
				else:
					features[(str(history[0]),history[1],history[2])] += featuresGlobal[('TAG-WORD-1','STOP',history[2])]

				
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
					for L in range(-2,-(min(len(sentenceList[ctr][i]),4))-1,-1):
						suffix = sentenceList[ctr][i][L:]
						featuresGlobal[('SUFFIX',suffix,tagSequenceFinal[i])] -= 1.0
						featuresGlobal[('SUFFIX',suffix,sentenceTagList[ctr][i])] += 1.0
					if (i > 0 ):
						featuresGlobal[('TAG-WORD-1',sentenceList[ctr][i-1],tagSequenceFinal[i])] -= 1.0
						featuresGlobal[('TAG-WORD-1',sentenceList[ctr][i-1],sentenceTagList[ctr][i])] += 1.0
					else:
						featuresGlobal[('TAG-WORD-1','*',tagSequenceFinal[i])] -= 1.0
						featuresGlobal[('TAG-WORD-1','*',sentenceTagList[ctr][i])] += 1.0
					if ( i < len(sentenceList[ctr]) - 1):
						featuresGlobal[('TAG-WORD+1',sentenceList[ctr][i+1],tagSequenceFinal[i])] -= 1.0
						featuresGlobal[('TAG-WORD+1',sentenceList[ctr][i+1],sentenceTagList[ctr][i])] += 1.0
					else:
						featuresGlobal[('TAG-WORD+1','STOP',tagSequenceFinal[i])] -= 1.0
						featuresGlobal[('TAG-WORD+1','STOP',sentenceTagList[ctr][i])] += 1.0
						
					if ( i == 0):
						featuresGlobal[('BIGRAM','*',tagSequenceFinal[i])] -=  1.0
						featuresGlobal[('BIGRAM','*',sentenceTagList[ctr][i])] +=  1.0
					else:
						featuresGlobal[('BIGRAM',tagSequenceFinal[i-1],tagSequenceFinal[i])] -=  1.0
						featuresGlobal[('BIGRAM',sentenceTagList[ctr][i-1],sentenceTagList[ctr][i])] +=  1.0
			#else:
			#	if len(sentenceTagList[ctr]) > 10:
			#		print ctr 
			#		print finalFeatureList


	for key in featuresGlobal:
		val = key
		if featuresGlobal[key] != 0:
			print (val[0] + ':' + val[1] + ':' + val[2] + ' ' + str(featuresGlobal[key]))
	#print str(sanity)
		




				
		



if __name__ == '__main__':
	trainFile = open('tag_train.dat','r')
	featureFile = open('suffix_tagger.model','r')
	
	readTrainFile(trainFile.read().splitlines())
	#readFeatures(featureFile)
	
	#readDevFile(devFile.read().splitlines())

