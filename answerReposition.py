import json
import sys
sys.path.insert(0,'Lib')

import re

import nltk

### FILE READ ###

with open(sys.argv[1],"r") as finDevPar:
    devParData = json.load(finDevPar)

fout = open(sys.argv[2],"w")

passAnsNum =0
passQueNum =0
passParNum  =0
# read paragraph data, make dic
jsonData=[]
version = devParData["version"]
qidDic = {}
for i in range(len(devParData["data"])):
	title = devParData["data"][i]["title"]
	jsonParagraph = []
	for j in range(len(devParData["data"][i]["paragraphs"])):
		contextPar = devParData["data"][i]["paragraphs"][j]["context"]
		# FOR EACH SENTENCE
		preConIndex = 0
		preConIndexBackup = 0
		jsonQas = []
		for l in range(len(devParData["data"][i]["paragraphs"][j]["qas"])):
			question = devParData["data"][i]["paragraphs"][j]["qas"][l]["question"]
			qid = devParData["data"][i]["paragraphs"][j]["qas"][l]["id"]
			# FOR EACH ANSWER
			answerDic = {}
			jsonAnswers = []
			for m in range(len(devParData["data"][i]["paragraphs"][j]["qas"][l]["answers"])):
				answerStart=devParData["data"][i]["paragraphs"][j]["qas"][l]["answers"][m]["answer_start"]
				answerText=devParData["data"][i]["paragraphs"][j]["qas"][l]["answers"][m]["text"]
				if(contextPar[int(answerStart):int(answerStart)+len(answerText)]!=answerText):
					print("answerstartchange")
					print(answerStart)
					answerStart = contextPar[:min(len(contextPar),int(answerStart)+2*len(answerText))].rfind(answerText)
					print(answerStart)

				if(contextPar[int(answerStart):int(answerStart)+len(answerText)]!=answerText):
					print("Error detected")
					print(answerText)

				jsonAnswers.append({"answer_start":answerStart, "text":answerText})
			jsonQas.append({"answers":jsonAnswers,"question":question,"id":qid})
		jsonParagraph.append({"context":contextPar,"qas":jsonQas})
	jsonData.append({"title":title,"paragraphs":jsonParagraph})
fout.write(json.dumps({"data":jsonData,"version":version}))
finDevPar.close()
fout.close()
		
