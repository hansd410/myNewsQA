#-*- coding: utf-8 -*-
import csv
import re
import json
import sys

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

docIdDic = {}
jsonQas={}
storyTextDic = {}

for i in range(len(matrix)):
    if i ==0:
        continue
    else:
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

        if(docIdDic[story_id]==0):
            storyTextDic[story_id]=story_text

        ##### GET ANSWER #####

        answerList = []
        answerStartList = []
        for j in range(len(endIndexList)):
            endIndex = endIndexList[j]
            beginIndex = beginIndexList[j]
            answer = story_text [ beginIndex : endIndex ]
            answerList.append(answer)
            answerStartList.append(beginIndex)

        ##### print to JSON #####

        jsonAnswers=[]
        print("len answerList:"+str(len(answerList))+":")
        for j in range(len(answerList)):
            if(answerList[j]!="" and answerList[j]!=" "):
                print ("j is :"+str(j)+":")
                jsonAnswers.append({"answer_start":answerStartList[j],"text":answerList[j]})
        if (len(jsonAnswers)>0):
            if(docIdDic[story_id]==0):
                jsonQas[story_id]=[]
                jsonQas[story_id].append({"answers":jsonAnswers,"question":questions,"id":story_id+str(docIdDic[story_id])})
                docIdDic[story_id]=docIdDic[story_id]+1
            else:
#                 jsonQas[story_id].append({"test"})
                jsonQas[story_id].append({"answers":jsonAnswers,"question":questions,"id":story_id+str(docIdDic[story_id])})
                docIdDic[story_id]=docIdDic[story_id]+1

jsonData = []
for key in jsonQas:
    jsonParagraph=[]
#    fout.write("appending key:"+key+":")
#    fout.write("context:"+storyTextDic[key]+":")
#    fout.write("qas:"+str(jsonQas[key])+":")
    jsonParagraph.append({"context":storyTextDic[key],"qas":jsonQas[key]})
    jsonData.append({"title":"nonTitle","paragraphs":jsonParagraph})

#print ("json Data print..\n")
#print jsonData
print ("file writing...\n")
fout.write(json.dumps({"data":jsonData,"version":"NewsQA1.0"},ensure_ascii=False))

fout.close()
