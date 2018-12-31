#-*- coding: utf-8 -*-
#V2 : sentence is not splited, use csv story id`
import csv
import re
import json
import sys
import nltk
import codecs

###### READ FILE ######

fin = open(sys.argv[1],'r')
fout = codecs.open(sys.argv[2],"w",'utf-8')

json_data = json.dumps({})

csvReader = csv.reader(fin)

matrix = []
rowNum  = 0
for row in csvReader:
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

		indexToken = answer_char_ranges.split('|')

		##### GET ANSWER INDEX THROUGH SPACE PROCESSING #####

		beginIndexList = []
		endIndexList = []

		for j in range(len(indexToken)):
			index = indexToken[j].split(':')
			beginIndex = int(index[0])
			endIndex = int(index[1])
			beginIndexList.append(beginIndex)
			endIndexList.append(endIndex)

		answerList = is_answer_absent.split("||")

		# CHECK WHETHER INDEX AND ANSWER ARE SYNCED
		#storyTemp = story_text.decode('utf-8')
		#storyAscii = storyTemp.encode('ascii')
		for j in range(len(beginIndexList)):
			if(story_text[beginIndexList[j]:endIndexList[j]] != answerList[j]):
				print(str(story_id)+"answer is not synced")
				print(story_text[beginIndexList[j]:endIndexList[j]])
				print(answerList[j])

#				beginIndexList[j] = story_text[max(0,beginIndexList[j]-len(answerList[j])):min(beginIndexList[j]+len(answerList[j]),len(story_text))].find(answerList[j])


		##### put all data into dic #####
		if(story_id not in qaDic.keys()):
			qaDic[story_id] = []
			qaDic[story_id].append((questions,answerList,beginIndexList))
		else:
			qaDic[story_id].append((questions,answerList,beginIndexList))
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
			answerStart = qaDic[key][i][2][j]	
			answer= qaDic[key][i][1][j]
			answerBeginning = contextDic[key][:int(answerStart)+1]
#			answerStart = str(len(contextDic[key][:int(answerStart)+1].encode('ascii'))-1)


#			if(contextDic[key][:int(answerStart)+1]):
#				print(contextDic[key][int(answerStart):(int(answerStart)+len(answer))])
#				print(answer)
#				print ("error")
#				exit()
#			if(contextDic[key][max(0,int(answerStart)-len(answer)),min(len(contextDic[key],int(answerStart)+len(answer))]!=answer):

#			try:
#				jsonTemp = json.dumps(answerBeginning)
#			except:
#				print ("passed")
#				continue
#			jsonAnswers.append({"answer_start":len(jsonTemp),"text":answer})
			jsonAnswers.append({"answer_start":answerStart,"text":answer})

		if (len(jsonAnswers)>0):
			if (key not in keyCountDic.keys()):
				keyCountDic[key]=0
			else:
				keyCountDic[key]+=1
			jsonQas.append({"answers":jsonAnswers,"question":qaDic[key][i][0],"id":key+str(keyCountDic[key])})
	if(len(jsonQas)>0):
		jsonParagraph.append({"context":contextDic[key],"qas":jsonQas})

jsonData.append({"title":"nonTitle","paragraphs":jsonParagraph})
fout.write(json.dumps({"data":jsonData,"version":"NewsQA1.0"}))
fout.close()

