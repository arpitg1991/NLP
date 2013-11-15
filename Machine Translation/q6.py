import sys,math
import collections
import heapq as hq
from collections import defaultdict as dd
from sets import Set
englishParam =  dd(lambda: Set())
#tfe = dict()   
tfe = dd(lambda: dd(lambda: float(0))) #t(f|e)
cef = dd(float) #c(e,f)
ce = dd(float) # c(e)
cjilm = dd(float) # c(j|i,l,m)
cilm = dd(float) # c(i|l,m)
qjilm = dict() # q(j|i,l,m)
model1 = dict()

def alignments(english,german):
	english.seek(0,0)
	german.seek(0,0)
	outFile = open('alignmentsModel2.txt','w')
	for count in range(0,20):
		#print("sentence " + str(count) + '\n')
		sentenceEng = english.next()
		sentenceGer = german.next()
		outFile.write(sentenceEng)
		outFile.write(sentenceGer)
		sentenceEng = sentenceEng.strip()
		sentenceGer = sentenceGer.strip()
		englishTokens = sentenceEng.split()
		germanTokens = sentenceGer.split()
		M = len(germanTokens)
		L = len(englishTokens)
		alignmentsList = []
		
		englishTokens.insert(0,'NULL')
		for i in range(1,M+1):
			maxScoreIndex = 0
			maxScore = 0 
			#print ('j ')
			for j in range(0,L+1):
				score = qjilm[(j,i,L,M)] * tfe[germanTokens[i-1]][englishTokens[j]]
				#print (str(j) + ' ')
				if (score >= maxScore):
					maxScoreIndex = j
					maxScore = score
			#print ('\n')
			alignmentsList.append(maxScoreIndex)
		outFile.write(str(alignmentsList) + '\n')
		outFile.write('\n')

def readTParameters():
	inFile = open('TParameters.model2','r')
	for line in inFile:
		line = line.strip()
		line = line.split()
		entry = (line[0],line[1])
		tfe[line[0]][line[1]] = float(line[2])
		#model1[entry] = float(line[2])
	'''
	for ger in tfe:
		for eng in tfe[ger]:
			tfe[ger][eng] = model1[(ger,eng)]
	'''
def readQParameters():
	inFile  = open('QParameters.model2','r')
	for line in inFile:
		line = line.strip()
		line = line.split()
		entry = (int(line[0]),int(line[1]),int(line[2]),int(line[3]))
		qjilm[entry] = float(line[4])

def getBestEnglishSentence(scrambledEng, gerSentence):
	bestEnglish = ''
	bestEnglishScore = float(-sys.maxint)

	for engSentence in scrambledEng:
		engSentence = engSentence.strip()
		engTokens = engSentence.split()
		gerTokens = gerSentence.split()
		L = len(engTokens)
		M = len(gerTokens)
		scoreSentence = 0
		engTokens.insert(0,'NULL')
		for i in range(1,M+1):
			score = 0 
			bestAlignment = 0
			bestAlignmentScore = float(-sys.maxint)
			for j in range(0,L+1):
				qscore = -10000000
				tscore = -10000000
				if ((j,i,L,M) in qjilm):
					qscore = qjilm[(j,i,L,M)]
					if qscore > 0:
						qscore = math.log(qscore)
					else:
						qscore = -10000000
				if (gerTokens[i-1] in tfe):
					if(engTokens[j] in tfe[gerTokens[i-1]]):
						tscore = tfe[gerTokens[i-1]][engTokens[j]]
						if tscore > 0:
							tscore = math.log(tscore)
						else:
							tscore = -10000000
					
				score = qscore + tscore
				if ( score > bestAlignmentScore):
					bestAlignmentScore = score 
					bestAlignment = j
			scoreSentence = scoreSentence + bestAlignmentScore
		#print scoreSentence
		if ( scoreSentence >= bestEnglishScore ):
			bestEnglishScore = scoreSentence
			bestEnglish = engSentence
			#print(engSentence + '\n')
	return bestEnglish

def unscramble(scrambledEng,originalGerman):
	originalEnglish = open('unscrambled.en','w')
	for gerSentence in originalGerman:
		gerSentence = gerSentence.strip()
		scrambledEng.seek(0,0)
		bestEnglish = getBestEnglishSentence(scrambledEng,gerSentence)
		originalEnglish.write(bestEnglish)
		originalEnglish.write('\n')
	#close(originalEnglish)

	
if __name__ == '__main__':
	english = open('corpus.en')
	german = open('corpus.de')
	readTParameters()
	readQParameters()
	scrambledEng = open('scrambled.en')
	originalGerman = open('original.de')
	print('unscrambling')
	unscramble(scrambledEng,originalGerman)
