#-*- coding: utf-8 -*-
#V2 : sentence is not splited, use csv story id`
import csv
import re
import json
import sys
import nltk

###### READ FILE ######

fin = open(sys.argv[1],'r')
fout = open(sys.argv[2],"w")

json_data = json.dumps({})

csvReader = csv.reader(fin)

matrix = []
rowNum  = 0
for row in csvReader:
	print("rowNum:"+str(rowNum))
	matrix.append(row)
	rowNum += 1

###### PREPROCESS ######

jsonData = []
skipped = 0

qaDic = {}
contextDic = {}

questionNum = 0
questionWrittenNum =0

for i in range(len(matrix)):
	if i ==0:
		continue
	else:
		### PARSE ###
		story_id = matrix[i][0]

		questions = matrix[i][1]
		answer_char_ranges = matrix[i][2]
		is_answer_absent = matrix[i][3]
		is_question_bad = matrix[i][4]
		validated_answers = matrix[i][5]
		story_text = matrix[i][6]

		questionNum +=1
#		try:
#			story_text.decode('ascii')
#		except:
#			skipped += 1
#			continue
 #	   nltk.sent_tokenize(story_text)

		oldIndexToken = answer_char_ranges.split('|')
		indexToken = []
		for j in oldIndexToken:
			if j not in indexToken:
				indexToken.append(j)

		##### GET ANSWER INDEX THROUGH SPACE PROCESSING #####

		beginIndexList = []
		endIndexList = []

		for j in range(len(indexToken)):
			indexSubToken = indexToken[j].split(',')
			for k in range(len(indexSubToken)):
					index = indexSubToken[k].split(':')
					endIndex = int(index[1])
					endIndexList.append(endIndex)
					indexDiffer = int(index[1])-int(index[0])
					beginIndex = endIndex-indexDiffer
					beginIndexList.append(beginIndex)


		##### GET ANSWER #####

		answerList = []
		answerStartList = []
		for j in range(len(endIndexList)):
			endIndex = endIndexList[j]
			beginIndex = beginIndexList[j]
			answer = story_text [ beginIndex : endIndex ]
			answerList.append(answer)
			answerStartList.append(beginIndex)

		##### put all data into dic #####
		if(story_id not in qaDic.keys()):
			qaDic[story_id] = []
			qaDic[story_id].append((questions,answerList,answerStartList))
		else:
			qaDic[story_id].append((questions,answerList,answerStartList))
		contextDic[story_id] = story_text



##### PRINT JSON DATA #####
jsonData = []
jsonParagraph = []
keyCountDic = {}
for key in qaDic:
	jsonQas = []
#	try:
#		json.dumps({"context":contextDic[key]})
#	except:
#		continue
	for i in range(len(qaDic[key])):
		jsonAnswers = []
		for j in range(len(qaDic[key][i][1])):
			try:
				json.dumps({"answer_start":qaDic[key][i][2][j],"text":qaDic[key][i][1][j]})
			except:
				continue
			jsonAnswers.append({"answer_start":qaDic[key][i][2][j],"text":qaDic[key][i][1][j]})
		if (len(jsonAnswers)>0):
			try:
				json.dumps({"answers":jsonAnswers,"question":qaDic[key][i][0],"id":key})
			except:
				continue
			if (key not in keyCountDic.keys()):
				keyCountDic[key]=0
			else:
				keyCountDic[key]+=1
			jsonQas.append({"answers":jsonAnswers,"question":qaDic[key][i][0],"id":key+str(keyCountDic[key])})
	jsonParagraph.append({"context":contextDic[key],"qas":jsonQas})

jsonData.append({"title":"nonTitle","paragraphs":jsonParagraph})
fout.write(json.dumps({"data":jsonData,"version":"NewsQA1.0"}))
fout.close()

