# -*- coding: utf-8 -*-
# V2 : story id is given by processed csv file

import string
import csv
import io
import sys
import re
import os

if(not os.path.exists('data/preprocess')):
	os.mkdir('data/preprocess')
if(not os.path.exists('data/toJson')):
	os.mkdir('data/toJson')
if(not os.path.exists('data/result')):
	os.mkdir('data/result')

infilename = sys.argv[1]
outfilename = sys.argv[2]
passedNum =0
print("preprocess "+infilename+" begins")
with open(infilename, 'rb') as incsvfile:
	with open(outfilename, 'wb') as outcsvfile:
		reader = csv.DictReader(incsvfile, delimiter=',', quotechar='"')
		writer = csv.DictWriter(outcsvfile, fieldnames = reader.fieldnames)
		writer.writeheader()

		with io.open('lib/stories_requiring_extra_newline.csv', 'r', encoding="utf-8") as f:
			stories_requiring_extra_newline = set(f.read().split("\n"))
		with io.open('lib/stories_requiring_two_extra_newlines.csv', 'r', encoding="utf-8") as f:
			stories_requiring_two_extra_newlines = set(f.read().split("\n"))
		with io.open('lib/stories_to_decode_specially.csv', 'r', encoding="utf-8") as f:
			stories_to_decode_specially = set(f.read().split("\n"))

		docIdDic = {}
		for row in reader:
			# GOOD DATA FILTER
			if( (row['is_question_bad'] == '?')):
				passedNum += 1
				continue
			if((float(row['is_question_bad']) >= 0.5) or (float(row['is_answer_absent']) >= 0.5) ):
				passedNum += 1
				continue

			story_text = row['story_text']
			story_id = row['story_id']
			if(story_id not in docIdDic.keys()):
				docIdDic[story_id]=0

			question = row['question']

			if story_id in stories_requiring_two_extra_newlines:
				story_text = story_text.replace('\r\r\r\r\n', '   ')
			elif story_id in stories_requiring_extra_newline:
				story_text = story_text.replace('\r\r\r\n', '  ')
			else:
				story_text = story_text.replace('\r\r\n', ' ')

			if story_id in stories_to_decode_specially:
				story_text = filter(lambda x: x in string.printable, story_text)
				#story_text = story_text.replace('\xb2', '')
				#story_text = story_text.replace('\xe9', '\xc3\xa9')


			# GET NEW INDEX

			oldIndexToken = row['answer_char_ranges'].split('|')
			oldIndexTokenString = row['answer_char_ranges']
			indexToken = []
			for i in oldIndexToken:
				if i not in indexToken:
					indexToken.append(i)

			beginIndexList = []
			endIndexList = []
			newStoryText = re.sub("[ ]+"," ",story_text)
			storyTokenList = newStoryText.split(" ")
			for i in range(len(indexToken)):
				indexSubToken = indexToken[i].split(',')
				for k in range(len(indexSubToken)):
					if(indexSubToken[k]!="None"):
						index = indexSubToken[k].split(':')

						endIndex = len(re.sub("[ ]+"," ",story_text[:int(index[1])]))
						indexDiffer = int(index[1])-int(index[0])
						beginIndex = endIndex-indexDiffer

						# RE-ORGANIZE INDEX FOR 'n cuba'
						printString = ""
						beginToken=0
						endToken =0
						for l in range(len(storyTokenList)):
							if l ==0:
								endToken = len(storyTokenList[l])-1
							else:
								beginToken = endToken+2
								endToken += 1+ len(storyTokenList[l])
							if(endIndex<=endToken and endIndex>=float(beginToken+endToken)/2):
								endIndex = endToken+1
								printString += "tokenGiven1"
								printString += "\n"
								printString += storyTokenList[l-1]
								printString += "\n"
								printString += storyTokenList[l]
								printString += "\n"
								printString += newStoryText[beginIndex:endIndex]
								printString+="\n"

							elif(endIndex>=beginToken and endIndex<float(beginToken+endToken)/2):
								endIndex = beginToken-1
								printString += "tokenGiven2"
								printString += "\n"
								printString += storyTokenList[l-1]
								printString += "\n"
								printString += storyTokenList[l]
								printString += "\n"
								printString += newStoryText[beginIndex:endIndex]
								printString+="\n"

							if(beginIndex<=endToken and beginIndex>=float(beginToken+endToken)/2):
								printString += "check1"
								printString += "\n"
								printString += newStoryText[beginIndex:endIndex]
								printString+="\n"

								beginIndex = endToken + 2
							elif(beginIndex>=beginToken and beginIndex<float(beginToken+endToken)/2):
								printString += "check2"
								printString += "\n"
								printString += newStoryText[beginIndex:endIndex]
								printString+="\n"

								beginIndex = beginToken

						# RE-ORGANIZE FOR '"ANSWER'

						checkList = [' ',',','.','?','!','"',"'","[","]"]
						while(endIndex>beginIndex):
							if(newStoryText[endIndex-1] in checkList):
								endIndex = endIndex-1
							else:
								break

						while(beginIndex<endIndex):
							if(newStoryText[beginIndex] in checkList):
								beginIndex = beginIndex+1
							else:
								break
						if(beginIndex >=endIndex):
							continue
						
						endIndexList.append(endIndex)
						beginIndexList.append(beginIndex)


#			print("answer char range before:"+oldIndexTokenString)
#			print("after:"+newIndexToken)

			story_text = newStoryText
			row['story_text'] = story_text

			answersString = ""
			newIndexToken = ""
			for i in range(len(beginIndexList)):
				if(i==0):
					answersString = story_text[beginIndexList[i]:endIndexList[i]]
					newIndexToken = str(beginIndexList[i])+":"+str(endIndexList[i])
				else:					
					answersString += "||"+story_text[beginIndexList[i]:endIndexList[i]]
					newIndexToken += "|"+str(beginIndexList[i])+":"+str(endIndexList[i])
			

			row['is_answer_absent']=answersString
			row['answer_char_ranges'] = newIndexToken
			row['story_id'] = story_id
			if(newIndexToken=="" or answersString == ""):
				continue
			writer.writerow(row)
			docIdDic[story_id] += 1

print("passedNum")
print(passedNum)
print("preprocess "+infilename+" ends")

