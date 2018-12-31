#V1 : one context, one query, one answer

#-*- coding: utf-8 -*-
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
for row in csvReader:
    matrix.append(row)

###### PREPROCESS ######

docIdDic = {}
jsonQas={}
storyTextDic = {}
jsonData = []


for i in range(len(matrix)):
    if i ==0:
        continue
    else:
        print("rowNum:"+str(i))
        ### PARSE ###
        story_id = matrix[i][0]
        if(story_id not in docIdDic.keys()):
            docIdDic[story_id]=0

        questions = matrix[i][1]
        answer_char_ranges = matrix[i][2]
        is_answer_absent = matrix[i][3]
        is_question_bad = matrix[i][4]
        validated_answers = matrix[i][5]
        story_text = matrix[i][6]

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

        #if(docIdDic[story_id]==0):
        #    storyTextDic[story_id]=story_text

        ##### GET ANSWER #####

        answerList = []
        answerStartList = []
        for j in range(len(endIndexList)):
            endIndex = endIndexList[j]
            beginIndex = beginIndexList[j]
            answer = story_text [ beginIndex : endIndex ]
            answerList.append(answer)
            answerStartList.append(beginIndex)

        ##### sentence level context #####
        contextSen = nltk.sent_tokenize(story_text.decode('utf-8',errors='ignore'))
#        contextSen = nltk.sent_tokenize(story_text.decode('utf-8'))

        for j in range(len(beginIndexList)):
            preIndex = 0
            contextSenIndex = 0
            answer = answerList[j]
            loopExitFlag = 0
            beginIndex =0
            for k in range(len(contextSen)):
                preIndex += len(contextSen[k])
                if(k!=0):
                    preIndex += 1
                if(preIndex > beginIndexList[j]):
                    contextSenIndex = k
                    try:
                        beginIndex = contextSen[k].find(answer)
                    except:
                        loopExitFlag = 1
                        break
                    if(beginIndex>len(contextSen[k]) or beginIndex<0):
                        loopExitFlag = 1
                        break
                    beginIndexList[j]= beginIndex
                    break
                else:
                    loopExitFlag = 1
            if(loopExitFlag == 1):
                continue
				
            docIdDic[story_id]=docIdDic[story_id]+1

        ##### print to JSON #####
            jsonParagraph=[{"context":contextSen[contextSenIndex],"qas":[{"answers":[{"answer_start":beginIndexList[j],"text":answer}],"question":questions,"id":story_id+str(docIdDic[story_id])}]}]
            try:
                json.dumps({"paragraphs":jsonParagraph})
            except:
                continue
            jsonData.append({"title":"nonTitle","paragraphs":jsonParagraph})
            #print(jsonParagraph)
            #print(json.dumps({"paragraphs":jsonParagraph}))

#print ("json Data print..\n")
#print jsonData
#print ("file writing...\n")
#print(json.dumps({"data":jsonData,"version":"NewsQA1.0"},ensure_ascii=False))
fout.write(json.dumps({"data":jsonData,"version":"NewsQA1.0"}))

fout.close()
