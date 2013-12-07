from collections import defaultdict as dd 
from subprocess import PIPE
import sys, subprocess,sets
V = dd(float)
sentenceList = []

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


def readFeatures(featureFile):
	for line in featureFile:
		line = line.strip()
		tokens = line.split(' ')
		score = float(tokens[1])
		tokens = tokens[0].split(':')
		V[(tokens[0],tokens[1],tokens[2])] = score

def readDevFile(devFile):
	totalLines = len(devFile)
	ctr = 0
	while ctr < totalLines:
		sentence = []
		readMore = True
		sentence.append(devFile[ctr])
		ctr = ctr  + 1
		while(readMore and ctr < totalLines ):
			line = devFile[ctr]
			ctr += 1 
			lineStrip = line.strip()
			if (lineStrip):
				sentence.append(line)
			else:
				readMore = False
				sentence[len(sentence) - 1] = sentence[len(sentence) - 1 ].strip()
		sentenceList.append(sentence)
		#print sentence
	totalSentences = len(sentenceList)

	for ctr in range(0,totalSentences):
		#print sentenceList[ctr]
		sent = '\n'.join(sentenceList[ctr])
		enum_history = call(enum_server,sent)
		#print sent
		enum_history = enum_history.splitlines()
		#print enum_history
		#print len(enum_history)
		features = dict()
		tagsSet = set()
		for history in enum_history:
				#print history
				history = history.split()
				features[(str(history[0]),history[1],history[2])] = V[('BIGRAM',history[1],history[2])]
				features[(str(history[0]),history[1],history[2])] += V[('TAG',sentenceList[ctr][int(history[0]) - 1],history[2])]
				for i in range(-2,-(min(len(sentenceList[ctr][int(history[0]) - 1]),4))-1,-1):
					suffix = sentenceList[ctr][int(history[0]) - 1][i:]
					features[(str(history[0]),history[1],history[2])] += V[('SUFFIX',suffix,history[2])]
				wordIndex = int(history[0]) - 1
				if (wordIndex > 0 ):
					features[(str(history[0]),history[1],history[2])] += V[('TAG-WORD-1',sentenceList[ctr][wordIndex -1 ],history[2])]
				else:
					features[(str(history[0]),history[1],history[2])] += V[('TAG-WORD-1','*',history[2])]

				#for i in range(2,(min(len(sentenceList[ctr][int(history[0]) - 1]),4))+1,1):
				#	suffix = sentenceList[ctr][int(history[0]) - 1][:i]
				#	features[(str(history[0]),history[1],history[2])] += V[('PREFIX',suffix,history[2])]
			
		featureList = []
		for feature in features:
			unrollFeature = ' '.join(feature)
			unrollFeature = unrollFeature + ' ' + str(features[feature])
			featureList.append(unrollFeature)
		finalFeatureList = '\n'.join(featureList)
		
		#print finalFeatureList 
		
		tagSequence = call(decoder_server,finalFeatureList)
		#print'hello'
		#print tagSequence
		tagSequence = tagSequence.strip()
		tagSequence = tagSequence.split('\n')
		tagSequenceFinal = []
		for i in range(0,len(sentenceList[ctr])):
			tags = tagSequence[i].split()
			#print tags
			tagSequenceFinal.append(sentenceList[ctr][i] + ' ' + tags[2])
		tagSequenceFinal = '\n'.join(tagSequenceFinal)
		print tagSequenceFinal + '\n'
		




if __name__ == '__main__':
	featureFile = open('tag.model6','r')
	devFile = open('tag_dev.dat','r')
	readFeatures(featureFile)
	#print V
	readDevFile(devFile.read().splitlines())

