'''
IMPLEMENT VITERBI when words have been classified into categories
'''
'''
takes 2 files 1st must be ner.count
second must be ner_dev.dat
'''
import math
import sys
import re

tri_gram_dict = dict()
bi_gram_dict = dict()
viterbi_p = dict()
viterbi_bp = dict()
ne_dict = dict()
totalTags = []


'''
calculates e(x|y)
'''
def emission_param_eval(word,ne_tag):
    count_xy = 0
    if (word in ne_dict[ne_tag]):
        count_xy = (int)(ne_dict[ne_tag][word])
    count_y = ne_dict[ne_tag]['tot_occ_ne']
    return float(count_xy) /float(count_y)


'''
Given a word and a tag it calls emission_param_eval
to calculate e(x|y), but if a word is not seen before, then 
it replaces it with _RARE_ and then checks again for e(x|y)
'''
def calc_wrd_tag_prob(word,tag):
	prob = 0
	for ne_tag in ne_dict:
		prob_temp = emission_param_eval(word,ne_tag)
		if (prob_temp > prob ):
 			prob = prob_temp
	if (prob > 0): # word was not rare, and we should this word to calc probability not _RARE_
 		prob = emission_param_eval(word,tag)
	else: # the word was rare, we should use _CATEGORIES_ to calculate its prob
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
		m1 = num.search(word)
		m2 = allCaps.search(word)
		m3 = capsDash.search(word)
		m4 = alphaNum.search(word)
		m5 = abv.search(word)
		m6 = pn.search(word)

		if m1:
			prob = emission_param_eval('_NUM_',tag)
		elif m5:
			prob = emission_param_eval('_ABV_',tag)
		elif m3:
			prob = emission_param_eval('_CAPS-DASH_',tag)
		elif m6:
			prob = emission_param_eval('_PN_',tag)
		elif m4:
			prob = emission_param_eval('_ALPHANUM_',tag)
		elif m2:
			prob = emission_param_eval('_CAPS_',tag)
		else:
			prob = emission_param_eval('_RARE_',tag)
	return prob   

def create_ne_dict(inputFile):
    '''
    creates a dictionary of named entity pairs with keys as TAGS
    and each key has a list of members. Each member is itself a list 
    with first member as the word and seond as count of the times it appears
    with the TAG. For example one instance of this dict would like like  :
    
    {
    'I-ORG': {'University':13, 'Primedia':2 ..... } ,
    'I-PER', {'Solano':1, 'Willie':4.... },
    
    
    }
    
    at the end, dictionary is modified to include some meta information,
    which is, total number of times an entity occured. So dict finally looks like 
    
    {
    'I-ORG': {'University':13, 'Primedia':2 ....., 'tot_occ_ne':15 } ,
    'I-PER', {'Solano':1, 'Willie':4...., 'tot_occ_ne':5 },
    
    
    }
    
    '''
    
    for line in inputFile:
        line = line.strip()
        fields = line.split(" ")
        if (fields[1] == 'WORDTAG' ):
            if fields[2] in ne_dict:
                ne_dict[fields[2]][fields[3]] = (int)(fields[0])
            else:
                ne_dict[fields[2]] = dict()
                ne_dict[fields[2]][fields[3]] = (fields[0])

    for ne in ne_dict:
        sum_ne = 0
        for wrd in ne_dict[ne]:
            sum_ne += (int)(ne_dict[ne][wrd])
        ne_dict[ne]['tot_occ_ne'] = sum_ne
        print (ne + str(sum_ne))
    print ('length of dict' + str(len(ne_dict)))


'''
calculates probabilities
given a trigram y1,y2,y3
'''
def prob_trigram(y1,y2,y3):
	gram3 = " ".join([y1,y2,y3])
	gram2 = " ".join([y1,y2])
	count3 = 0
	prob = 0
	if gram3 in tri_gram_dict:
		count3 = int(tri_gram_dict[gram3])
		count2 = int(bi_gram_dict[gram2])
		prob = count3/float(count2)
	return prob

'''
creates a dictionary of trigrams
each trigram and its count is stored as key-value pair
'''
def tri_gram(file1):   
	for line in file1:
		line = line.strip()
		if line:
			token = line.split(" ")
			if (token[1] == "3-GRAM"):
				gram3 = " ".join([token[2],token[3],token[4]])
				tri_gram_dict[gram3] = int(token[0])

'''
creates a dictionary of bigrams
each bigram and its count is stored as key-value pair
'''
def bi_gram(file1):
	for line in file1:
		line = line.strip()
		if line:
			token = line.split(" ")
			if (token[1] == "2-GRAM"):
				gram2 = " ".join([token[2],token[3]])
				bi_gram_dict[gram2] = int(token[0])


'''
creates a list of all tags
the taglist = {*, all tags seens in training}
'''
def create_tagList():
	totalTags.append('*')
	for tag in ne_dict:
		totalTags.append(tag)

'''
creates a DP "array"(in the meaning it is used in c/c++)
at level k = 0 , all tag pairs have initial prob = -maxint
except viterbi_p[k][0]['*']['*'] = 1 

at other levels viterbi_p[k][][] = -MaxInt for all pairs

viterbi_bp is initialised to viterbi_bp[k][][] = '' 
for all levels , all pairs of tags. viterbi_bp[0] is created but not used
anywhere, it is created just to simplify this creation process, could have been avoided
'''
def initialise(k):
	if ( k == 0 ):
		viterbi_p.clear()
		viterbi_bp.clear()
	viterbi_p[k] = dict()
	viterbi_bp[k] = dict()
	min1 = sys.maxint
	min1 = -min1
	for tags in totalTags:
		viterbi_p[k][tags] = dict()
		viterbi_bp[k][tags] = dict()
		for tags2 in totalTags:
			viterbi_p[k][tags][tags2] = min1
			viterbi_bp[k][tags][tags2] = ''
	if ( k == 0 ):
		viterbi_p[0]['*']['*'] = 1


'''
returns list of tokens allowed
for work K
'''
def validToken(K):
	valid = []
	if ( K < 1):
		valid.append('*')
	else:
		valid = totalTags[:]
		valid.pop(0)
	return valid

'''
Reads file ner_dev.dat
and outputs viterbi_results.dat
'''

def viterbi(file2):
	file4 = open("viterbi_results_q6.dat","w")
	log_prob_k = 1
	listTag = [] 
	listProb = []
	listToken = []
	k = 1
	initialise(0)
	for line in file2:
		initialise(k)
		line = line.strip()
		if line:
			listToken.append(line)
			listK_2 = validToken(k-2) 
			listK_1 = validToken(k-1)
			listK = validToken(k)
			for K_0 in listK:
				for K_1 in listK_1:
					for K_2 in listK_2:
						val_log_prob = viterbi_p[k-1][K_1][K_2] * prob_trigram(K_2,K_1,K_0) * calc_wrd_tag_prob(line,K_0)
						if( viterbi_p[k][K_0][K_1] < val_log_prob):
							viterbi_p[k][K_0][K_1] = val_log_prob
							viterbi_bp[k][K_0][K_1] = K_2
			k = k +1 


			
		else: #empty line , denotes end of sentence, now we need to use back pointers, to construct list of tags
			
			N = k-1
			#print(N)
			tagN = ''
			tangN_1 = ''
			listK_1 = validToken(N-1)
			listK = validToken(N)
			max1 = sys.maxint ;
			max1 = -max1
			for K_0 in listK:
				for K_1 in listK_1:
					if (viterbi_p[N][K_0][K_1]*prob_trigram(K_1,K_0,'STOP') > max1):
						tagN = K_0
						tagN_1 = K_1
						max1 = viterbi_p[N][K_0][K_1]
			listTag.append(tagN)
			listTag.append(tagN_1)
			listTag.append(viterbi_bp[N][tagN][tagN_1])
			listProb.append(max1)
			tagN = tagN_1
			tagN_1 = listTag[-1]	
			for i in range(1,N):  
				listTag.append(viterbi_bp[N-i][tagN][tagN_1])
				listProb.append(viterbi_p[N-i][tagN][tagN_1])
				tagN = tagN_1
				tagN_1 = listTag[-1]
			rem = listTag.pop() #removes * symbol for tag at pos 0 
			rem = listTag.pop() #removes * symbol for tag at pos -1
			#as tags and prob have been obatained in a reverse order, we need to reverse these lists
			listTag.reverse()
			listProb.reverse()
			prob = 0
			for i in range(0,len(listToken)):
				#print(str(len(listToken)) + " " + str(len(listProb)) + " " + str(len(listTag)))
				prob = prob +  math.log(listProb[i],2)
				#print(prob)
				#logProb = math.log(prob,2)
				file4.write(listToken[i] + " " + listTag[i] + " " + str(prob) + "\n")
			file4.write("\n")
			prob = 1 #empty line, now we need to start fresh to set log_prob to 1
			initialise(0)  #also DP array also needs to be emptied, as we need to star with K=1 again
			k = 1
			listTag = []
			listProb = []
			listToken = []



'''
takes 2 files 1st must be ner.count
second must be ner_dev.dat
'''

if __name__ == "__main__":

	if (len(sys.argv)!= 3): #first file must be ner.count and second file must be ner_dev.dat
		sys.exit(2)
	try:
		file1 = file(sys.argv[1],"r")
		file2 = file(sys.argv[2],"r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile %s.\n" % arg)
		sys.exit(1)
	create_ne_dict(file1)
	file1.seek(0,0)
	tri_gram(file1)
	file1.seek(0,0)
	bi_gram(file1)
	create_tagList()
	viterbi(file2)
	#print_log_prob(file2) 








