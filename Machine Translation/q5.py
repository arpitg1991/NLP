import sys
import collections
import heapq as hq
from collections import defaultdict as dd
from sets import Set
englishParam =  dd(lambda: Set())
tfe = dd(lambda: dd(lambda: float(0))) #t(f|e)
cef = dd(float) #c(e,f)
ce = dd(float) # c(e)
cjilm = dd(float) # c(j|i,l,m)
cilm = dict() # c(i|l,m)
qjilm = dict() # q(j|i,l,m)
model1 = dict()

def initialiseParams(english,german):
	for sentenceEng in english:
		sentenceGer = german.next()
		sentenceEng = sentenceEng.strip()
		sentenceGer = sentenceGer.strip()
		engTokens = sentenceEng.split()
		gerTokens = sentenceGer.split()
		engTokens.append('NULL')
		
		for tokenEng in engTokens:
			for tokenGer in gerTokens:
				englishParam[tokenEng].add(tokenGer)

	english.seek(0,0)
	german.seek(0,0)
		

	for sentenceEng in english:
		sentenceGer = german.next()
		sentenceEng = sentenceEng.strip()
		sentenceGer = sentenceGer.strip()
		engTokens = sentenceEng.split()
		gerTokens = sentenceGer.split()
		M = len(gerTokens)
		L = len(engTokens) 
		for i in range(1,M+1):
			for j in range(0,L+1):
				qjilm[(j,i,L,M)] = 1.0/float(L+1)
		engTokens.append('NULL')
		for token in gerTokens:
			for tokenEng in engTokens:
				tfe[token][tokenEng] = 1.0/ float ( len(englishParam[tokenEng]) ) 
				

def em(english,german):
	cef.clear()
	ce.clear()
	cjilm.clear() # c(j|i,l,m)
	cilm.clear() # c(i|l,m)
	for sentenceEng in english:
		sentenceGer = german.next()
		sentenceEng = sentenceEng.strip()
		sentenceGer = sentenceGer.strip()
		engTokens = sentenceEng.split()
		gerTokens = sentenceGer.split()
		M = len(gerTokens)
		L = len(engTokens)
		engTokens.insert(0,'NULL')
		delta = dd(lambda: dd(lambda: float(0)))
		for i in range(1,M+1):
			sumIJ = 0.0
			for j  in range(0,L+1):
				delta[i][j] = qjilm[(j,i,L,M)]*tfe[gerTokens[i-1]][engTokens[j]]
				sumIJ = sumIJ + delta[i][j]
			
			for j in range(0,L+1):
				delta[i][j] = delta[i][j] / float(sumIJ)
				
		for i in range(1,M+1):
			for j in range(0,L+1):
				if ((engTokens[j],gerTokens[i-1]) in cef):
					cef[(engTokens[j],gerTokens[i-1])] = cef[(engTokens[j],gerTokens[i-1])] + delta[i][j]
				else:
					cef[(engTokens[j],gerTokens[i-1])] = delta[i][j]
				if (engTokens[j] in ce):
					ce[engTokens[j]] = ce[engTokens[j]] + delta[i][j]
				else:
					ce[engTokens[j]] = delta[i][j]
				if ((j,i,L,M) in cjilm):
					cjilm[(j,i,L,M)] = cjilm[(j,i,L,M)] + delta[i][j]
				else:
					cjilm[(j,i,L,M)] = delta[i][j]
				if ((i,L,M) in cilm):
					cilm[(i,L,M)] = cilm[(i,L,M)] + delta[i][j]
				else:
					cilm[(i,L,M)] = delta[i][j]
	for ger in tfe:
		for eng in tfe[ger]:
			if ((eng,ger) in cef):
				#and ce[eng] != 0):
				tfe[ger][eng] = cef[(eng,ger)] / ce[eng]

	for key in qjilm:
		#print key,str(cjilm[key])
		#print str(cilm[(key[1],key[2],key[3])])
		qjilm[key] = cjilm[key] / cilm[(key[1],key[2],key[3])]
		
def runEM(iter,english,german):
	for i in range(0,iter):
		english.seek(0,0)
		german.seek(0,0)
		em(english,german)

def top10Words(englishWord):
	outfile = open('topWords.model2','w')
	h = []
	for french in tfe:
		if(englishWord in tfe[french]):
			hq.heappush(h,(tfe[french][englishWord],french))
	top10 = hq.nlargest(10,h)
	topFrench = []
	for (score,word) in top10:
		topFrench.append((word,score))
	outfile.write(englishWord + '\n')
	outfile.write(str(topFrench) + '\n')
	outfile.write('\n')

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

def outputTParameters():
	outFile = open('TParameters.model2','w')
	for ger in tfe:
		for eng in tfe[ger]:
			outFile.write(ger + ' ' + eng + ' ' + str(tfe[ger][eng]) + '\n')

def outputQParameters():
	outFile = open('QParameters.model2','w')
	for key in qjilm:
		outFile.write(str(key[0]) + ' ' + str(key[1]) + ' ' + str(key[2]) + ' ' + str(key[3]) + ' ' + str(qjilm[key]) + '\n')

def readTParameters():
	inFile = open('TParameters.model1','r')
	for line in inFile:
		line = line.strip()
		line = line.split()
		entry = (line[0],line[1])
		tfe[line[0]][line[1]] = float(line[2])
def readQParameters():
	inFile  = open('QParameters.model1','r')
	for line in inFile:
		line = line.strip()
		line = line.split()
		entry = (int(line[0]),int(line[1]),int(line[2]),int(line[3]))
		qjilm[entry] = float(line[4])
	

def top10germanWords(wordsFile):
	outfile = open('topWords.model2','w')
	for word in wordsFile:
		englishWord = word.strip()
		h = []
		for french in tfe:
			#print(h,(tfe[french][englishWord],french))
			if(englishWord in tfe[french]):
				hq.heappush(h,(tfe[french][englishWord],french))
		top10 = hq.nlargest(10,h)
		topFrench = []
		for (score,word) in top10:
			topFrench.append((word,score))
		outfile.write(englishWord + '\n')
		outfile.write(str(topFrench) + '\n')
		outfile.write('\n')
	
if __name__ == '__main__':
	english = open('corpus.en')
	german = open('corpus.de')
	initialiseParams(english,german)
	#print 'hello',str(tfe['polizei'][','])
	readTParameters()
	#readQParameters()
	runEM(5,english,german)
	wordsFile = open('devwords.txt')
	top10germanWords(wordsFile)
	alignments(english,german)
	outputTParameters()
	outputQParameters()