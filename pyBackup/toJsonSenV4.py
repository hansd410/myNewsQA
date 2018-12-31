# V3 : one context, one query, multi answers + use csv's qid
# new qid for sentence (_senid is added)

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
#        contextSen = nltk.sent_tokenize(story_text.decode('utf-8',errors='ignore'))
#        contextSen = nltk.sent_tokenize(story_text.decode('utf-8'))
        try:
            contextSen = nltk.sent_tokenize(story_text)
        except:
            continue

        preIndex = [0,0]
        for j in range(len(contextSen)):
            try:
                contextSen[j].decode('ascii')
            except:
                continue
            if(j == 0):
                preIndex[1] += len(contextSen[j])
            if(j == 1):
                preIndex[0] += len(contextSen[j-1])
                preIndex[1] += len(contextSen[j])+1
            else:
                preIndex[0] += len(contextSen[j-1])+1
                preIndex[1] += len(contextSen[j])+1

            beginListIndex = []
            for k in range(len(beginIndexList)):
                if(beginIndexList[k]>preIndex[0] and beginIndexList[k]<preIndex[1]):
                    beginListIndex.append(k)

            jsonAnswers = []
            jsonParagraph = []
            for k in beginListIndex:
                answer = answerList[k]
                try:
                    beginIndex = contextSen[j].find(answer)
                except:                  
                    continue
                if(beginIndex > len(contextSen[j]) or beginIndex<0):
                    continue
                try:
                    json.dumps({"answer_start":beginIndex,"text":answer})
                except:
                    continue
                jsonAnswers.append({"answer_start":beginIndex,"text":answer})

            if(len(jsonAnswers)>0):
                tempStoryId = story_id+str("_")+str(docIdDic[story_id])
        ##### print to JSON #####            
                jsonParagraph=[{"context":contextSen[j],"qas":[{"answers":jsonAnswers,"question":questions,"id":tempStoryId}]}]
                docIdDic[story_id]=docIdDic[story_id]+1

            else:
                continue
            try:
                json.dumps({"paragraphs":jsonParagraph})
            except:
                continue
            jsonData.append({"title":"nonTitle","paragraphs":jsonParagraph})


          
#print ("json Data print..\n")
#print jsonData
#print ("file writing...\n")
#print(json.dumps({"data":jsonData,"version":"NewsQA1.0"},ensure_ascii=False))
fout.write(json.dumps({"data":jsonData,"version":"NewsQA1.0"}))

fout.close()
