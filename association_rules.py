import csv, string, sys, re, random, itertools, numpy, operator, itertools
from collections import Counter
from collections import defaultdict
from datetime import datetime

# Jason Martins - jmar316
# Association Rules practice

#####################################
def csv2LISTDICT(file_arg):
	#	Local Variables
	table_list = []						# our result of a list of dictionaries
	temp_row = {}  						# hold our temp rows
	
	#	Begin
	file = open(file_arg)
	data = csv.reader(file)
	
	for row in data:
		if data.line_num == 1: 			# Extract header line to be used in zip later
			file_header = row
		else:
			temp_row = dict(zip(file_header, row))
			# Remove punctuation (incl. \n) &  mark lower case
			temp_row["text"] = string.replace(temp_row["text"],'.',' ')
			temp_row["text"] = temp_row["text"].translate(None, string.punctuation)
			temp_row["text"] = temp_row["text"].lower()
			temp_row["text"] = string.replace(temp_row["text"],'\n',' ')
			table_list.append(temp_row)
	
	return table_list
#####################################
def freqCOUNT(table,reviewCount):
	# Iterates through all reviews and determines whether or not the 
	# review was positive or negative as determined by the class variable
	#  isPositive or isNegative
	
	#	Local Variables
	bag_of_words = ''
	binFeatHeadings = []
	
	#	Begin - create one giant string
	for i in range(len(table)):
		bag_of_words = ''.join([table[i]["text"],bag_of_words])
	
	# Create our big bag of words (only grab 201-2200)
	if reviewCount == 20:
		counter_result = Counter(re.findall(r'\w+',bag_of_words)).most_common()[201:209]
		features = 8
	else:
		counter_result = Counter(re.findall(r'\w+',bag_of_words)).most_common()[100:2100]
		features = 2000
	
	
	for i in range(features):
		binFeatHeadings.append(counter_result[i][0])
		
	binFeatHeadings.append('isPositive')
	binFeatHeadings.append('isNegative')

	pos_index = binFeatHeadings.index('isPositive')
	neg_index = binFeatHeadings.index('isNegative')
	
	binFeatures = numpy.zeros(shape=(reviewCount,features+2))
	
	# Iterate through all reviews
	for i in range(len(table)): 			
		review_split = grepString(table[i]["text"])
		stars_value = table[i]['stars']
		for word in review_split:
			for j in range(len(binFeatHeadings)):
				if word == binFeatHeadings[j]:
					binFeatures[i][j] = 1
		if stars_value == '5':
			binFeatures[i][pos_index] = 1
		else:
			binFeatures[i][neg_index] = 1

	return binFeatHeadings, binFeatures

#####################################	
def grepString(text):
	# Will take a review and return all words in that review, separated
	review_vector = re.findall(r'\w+',text,flags=re.I)
	return review_vector

#####################################
def freqItemSetGen(colHeadings,featMTRX,support_percnt):
	# My implementation of the Apriori association rule algorithm
	
	worst = 0
	isNegative = 0
	for i in range(len(colHeadings)):
		if colHeadings[i] == 'worst':
			worst = i
			print 'value of worst is', worst
		elif colHeadings[i] == 'isNegative':
			isNegative = i
			print 'value of isNegative is', isNegative
			
	row_worst = featMTRX[:,worst]
	row_isNegative = featMTRX[:,isNegative]
	
	#iterate through all reviews and determine true/false combinations
	count11 = 0 
	count10 = 0
	count01 = 0
	count00 = 0
	for i in range(len(row_worst)):
		if row_worst[i] == 1 and row_isNegative[i] == 1:
			count11 += 1
		elif row_worst[i] == 1 and row_isNegative[i] == 0:
			count10 += 1
		elif row_worst[i] == 0 and row_isNegative[i] == 1:
			count01 += 1
		elif row_worst[i] == 0 and row_isNegative[i] == 0:
			count00 += 1		
			
	support = []
	denominator = len(featMTRX)
	support_return = {}
	
	#########
	#Take entire dataset D and calculate support for all features
	#########
	for i in range(len(colHeadings)):
		numerator = sum(featMTRX[:,i])
		support.append((numerator/denominator))
	
	#########
	# Generate l1 which will have item sets of size one that meet the support thresh
	#########
	count = 0
	l1 = []
	for i in range(len(support)):
		
		if support[i] >= support_percnt:
			count += 1
			l1.append(i)
	print 'Question b(i): itemset1 met support =>',len(l1)
	print 'Question b(ii): itemset1 did not meet support =>',(len(support)-len(l1))
	#########
	# l1 contains indexes that reference the features in the original dataset
	# so l1_itemset will actually hold itemset of size 1 but with the actual
	# feature names
	#########
	
	l1_itemset = []
	for i in range(len(l1)):
		l1_itemset.append(colHeadings[l1[i]])
	
	
	#########	
	# now that we know which itemsets of size one meet the support threshold
	# we move on to candidates of size 2, here we generate all possible combos
	#########
	
	c2 = []
	count = 1
	for i in range(len(l1)):
		for j in range(count,len(l1)):
			if i < j:
				c2.append((l1[i],l1[j]))
		count += 1			
	
	print 'Number of Candidates possible itemsize 2:', len(c2)
	#########
	# now we must reference the original dataset and see if all these candidates 
	# are in the original, c2 is a list of tuples
	#########
	
	dne_list = []
	for i in range(len(c2)):
		feat1 = c2[i][0]  # references index of column feature heading(s)
		feat2 = c2[i][1]
		count = 0
		flag = 'N'
		while count != len(featMTRX):
			if featMTRX[count][feat1] == 1 and featMTRX[count][feat2] == 1:
				flag = 'Y'
				break
			count += 1
		if flag == 'N':
			dne_list.append(c2[i]) # storing tuple that needs to be removed
			
	for i in dne_list:  # remove item sets that are not found in D
		c2.remove(i)	
	
	print 'Number of possible size two that have been removed:', len(dne_list)
	
	
	#########
	#calculate support for c2
	#Take entire dataset D and calculate support for all features
	#########
	support_l2 = {}
	l2 = []
	l2_itemset = []
	for i in range(len(c2)):
		support_l2[c2[i]] = 0
		feat1 = c2[i][0]  # references index of column feature heading(s)
		feat2 = c2[i][1]
		
		for j in range(len(featMTRX)):
			if featMTRX[j][feat1] == 1 and featMTRX[j][feat2] == 1:
				support_l2[c2[i]] = support_l2[c2[i]] + 1
		
		numerator = support_l2[c2[i]]
		support_l2[c2[i]] = (float(numerator)/float(denominator))
		
		if support_l2[c2[i]] >= support_percnt: #Setup l2, if support thresh is met
			l2.append(c2[i])
			l2_itemset.append((colHeadings[c2[i][0]],colHeadings[c2[i][1]]))
			support_return[(colHeadings[c2[i][0]],colHeadings[c2[i][1]])] = support_l2[c2[i]]
			#print colHeadings[c2[i][0]],'->',colHeadings[c2[i][1]],'Support threshold:',support_l2[c2[i]]
	print 'Question b(i): itemset2 met support =>', len(l2)
	print 'Question b(ii): itemset2 did not meet support =>', (len(c2)-len(l2))
	
	
	#########	
	# now that we know which itemsets of size 2 meet the support threshold
	# we move on to candidates of size 3, here we generate all possible combos
	#########
	
	c3 = []
	presupport = 0
	for i in range(len(l2)):  # list of tuples of size two
		feat1 = l2[i][0] # indexes that refer to colHeadings
		feat2 = l2[i][1]
		matches = [(feat1,) + x for x in l2 if x[0] == feat2] #create our item 3 sets
		presupport += len(matches)
		for j in range(len(matches)):
			subset = (matches[j][0],matches[j][2])
			#if support_l2[subset] >= support_percnt:
			c3.append(matches[j])	
	print 'Number of Candidates possible itemsize 3: ', len(l2)
	print 'Number of Candidates possible itemsize 3 after pruning:', len(c3)
	#########
	#calculate support for c3
	#Take entire dataset D and calculate support for all features
	#########
	support_l3 = {}
	l3 = []
	l3_itemset = []
	for i in range(len(c3)):
		support_l3[c3[i]] = 0
		feat1 = c3[i][0]  # references index of column feature heading(s)
		feat2 = c3[i][1]
		feat3 = c3[i][2]
		
		for j in range(len(featMTRX)):
			if featMTRX[j][feat1] == 1 and featMTRX[j][feat2] == 1 and featMTRX[j][feat3] == 1:
				support_l3[c3[i]] = support_l3[c3[i]] + 1
		
		numerator = support_l3[c3[i]]
		support_l3[c3[i]] = (float(numerator)/float(denominator))
		
		if support_l3[c3[i]] >= support_percnt: #Setup l2, if support thresh is met
			l3.append(c3[i])
			l3_itemset.append((colHeadings[c3[i][0]],colHeadings[c3[i][1]],colHeadings[c3[i][2]]))
			#print colHeadings[c3[i][0]],'AND',colHeadings[c3[i][1]],'->',colHeadings[c3[i][2]],'Support threshold:',support_l3[c3[i]]
			support_return[(colHeadings[c3[i][0]],colHeadings[c3[i][1]],colHeadings[c3[i][2]])] = support_l3[c3[i]]
	print 'Question b(i): itemset3 met support =>', len(l3)
	print 'Question b(ii): itemset3 did not meet support =>', (len(c3)-len(l3)) 
	
	
	return l1,l2,l3,support_return

#####################################			
def ruleGen(colHeadings,featMTRX,itemsets,conf_percnt):
	# Function to generate final rule sets
	
	finalRule = {}
	
	for i in range(1,len(itemsets)):
		H = itemsets[i]
		
		for j in range(len(H)):
			itemset = H[j] # a tuple index
			if len(itemset) == 2:
				feat1 = itemset[0]
				feat2 = itemset[1]
				
				# rule1 if feat1 -> feat2
				# fr(feat1 & feat2)
				transpose = featMTRX[:,(feat1,feat2)]
				freq2feat = len([x for x in transpose if sum(x) == 2])
				
				# fr(feat1)
				freq1feat = sum(featMTRX[:,feat1])	
				
				if (float(freq2feat)/float(freq1feat)) >= conf_percnt:
					finalRule[(colHeadings[feat1],colHeadings[feat2])] = (float(freq2feat)/float(freq1feat))
					#print colHeadings[feat1],'->',colHeadings[feat2],'met confidence threshold:',(float(freq2feat)/float(freq1feat))
				
				# rule2 if feat2 -> feat1
				# fr(feat2 & feat1)
				# Calculated above
							
				# fr(feat2)
				freq1feat = sum(featMTRX[:,feat2])	
				
				if (float(freq2feat)/float(freq1feat)) >= conf_percnt:
					finalRule[(colHeadings[feat2],colHeadings[feat1])] = (float(freq2feat)/float(freq1feat))
					#print colHeadings[feat2],'->',colHeadings[feat1],'met confidence threshold:',(float(freq2feat)/float(freq1feat))
			
			else:
				feat1 = itemset[0]
				feat2 = itemset[1]
				feat3 = itemset[2]
				
				
				# rule1 if feat1 and feat2 -> feat3
				# fr(feat1 & feat2 & feat3)
				transpose = featMTRX[:,(feat1,feat2,feat3)]
				freq3feat = len([x for x in transpose if sum(x) == 3])
				
				
				# fr(feat1 & feat2)
				transpose = featMTRX[:,(feat1,feat2)]
				freq2feat = len([x for x in transpose if sum(x) == 2])
				
				if (float(freq3feat)/float(freq2feat)) >= conf_percnt:
					finalRule[(colHeadings[feat1],colHeadings[feat2],colHeadings[feat3])]= (float(freq3feat)/float(freq2feat))
				
				
				# rule2 if feat1 and feat3 -> feat2
				# fr(feat1 & feat2 & feat3)
				# Calculated above
				
				# fr(feat1 & feat3)
				transpose = featMTRX[:,(feat1,feat3)]
				freq2feat = len([x for x in transpose if sum(x) == 2])
				
				if (float(freq3feat)/float(freq2feat)) >= conf_percnt:
					finalRule[(colHeadings[feat1],colHeadings[feat3],colHeadings[feat2])] = (float(freq3feat)/float(freq2feat))
				
				# rule3 if feat3 and feat2 -> feat1
				
				# fr(feat1 & feat2 & feat3)
				# Calculated above
				
				# fr(feat3 & feat2)
				transpose = featMTRX[:,(feat3,feat2)]
				freq2feat = len([x for x in transpose if sum(x) == 2])
				
				if (float(freq3feat)/float(freq2feat)) >= conf_percnt:
					finalRule[(colHeadings[feat3],colHeadings[feat2],colHeadings[feat1])] = (float(freq3feat)/float(freq2feat))
	


	return finalRule
#####################################			
	
def sortedDict(ruleDict,support_return):
	# Sorts a dictionary for output
	
	count = 0
	for key,value in sorted(ruleDict.iteritems(),key=lambda (k,v): (v,k),reverse=True):
    		count += 1
    		print key,'-> Confidence',value,'Support:',support_return[key]
    		if count >= 30:
    			break


######## Main #########################################################################

####### BEGIN ################
# Capture arguments

starttime = datetime.now().time()
trainingDataFilename = sys.argv[1]
reviewCount = int(sys.argv[2])

#######################################################################################

# Input Set Processing
input_TABLE = csv2LISTDICT(trainingDataFilename)
binHeaders, binFeaturesMTRX = freqCOUNT(input_TABLE,reviewCount)
itemset1,itemset2,itemset3,support_return = freqItemSetGen(binHeaders,binFeaturesMTRX,0.03)

itemsets = []
itemsets.append(itemset1)
itemsets.append(itemset2)
itemsets.append(itemset3)

ruleset = ruleGen(binHeaders,binFeaturesMTRX,itemsets,0.25)
sortedDict(ruleset,support_return)
print 'Number of items passing support and confidence', len(ruleset.keys())
print 'Number of items passing support', len(itemset1)+len(itemset2)+len(itemset3)
print 'Start:', starttime
print 'Finish:', datetime.now().time()


	








