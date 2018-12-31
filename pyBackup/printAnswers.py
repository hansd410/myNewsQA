# -*- coding: utf-8 -*-
# V2 : story id is given by processed csv file

import string
import csv
import io
import sys
import re

infilename = sys.argv[1]
parNum =0
questionNum =0
answerNum=0
contextList = []
fout = open(sys.argv[2],'w')

with open(infilename, 'rb') as incsvfile:
	reader = csv.DictReader(incsvfile, delimiter=',', quotechar='"')
	docIdDic = {}
	for row in reader:
		story_text = row['story_text']
		story_id = row['story_id']
		if(story_id not in contextList):
			contextList.append(story_id)
		question = row['question']
		questionNum+=1
		answerList = row['answer_char_ranges'].split('|')
		fout.write(question)
		fout.write("\n")
#		print(answerList)
		for i in range(len(answerList)):
			if(answerList[i] == "None"):
				continue
			indexTokenList = answerList[i].split(',')

			for j in range(len(indexTokenList)):
				singleAnswerIndex = indexTokenList[j].split(':')
				beginIndex = int(singleAnswerIndex[0])
				endIndex = int(singleAnswerIndex[1])
				fout.write("["+str(beginIndex)+","+str(endIndex)+"]")
				fout.write(story_text[beginIndex:endIndex])
				fout.write("\n")
		fout.write(story_text)
		fout.write("\n\n")

parNum = len(contextList)

print("par")
print(parNum)
print("question")
print(questionNum)
