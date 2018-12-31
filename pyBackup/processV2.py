# -*- coding: utf-8 -*-
# V2 : story id is given by processed csv file

import string
import csv
import io
import sys
import re

infilename = sys.argv[1]
outfilename = sys.argv[2]
with open(infilename, 'rb') as incsvfile:
    with open(outfilename, 'wb') as outcsvfile:
        reader = csv.DictReader(incsvfile, delimiter=',', quotechar='"')
        writer = csv.DictWriter(outcsvfile, fieldnames = reader.fieldnames)
        writer.writeheader()

        with io.open('stories_requiring_extra_newline.csv', 'r', encoding="utf-8") as f:
            stories_requiring_extra_newline = set(f.read().split("\n"))
        with io.open('stories_requiring_two_extra_newlines.csv', 'r', encoding="utf-8") as f:
            stories_requiring_two_extra_newlines = set(f.read().split("\n"))
        with io.open('stories_to_decode_specially.csv', 'r', encoding="utf-8") as f:
            stories_to_decode_specially = set(f.read().split("\n"))

        docIdDic = {}
        for row in reader:
            # GOOD DATA FILTER
            if( (row['is_question_bad'] == '?')):
                continue
            if((float(row['is_question_bad']) >= 0.5) or (float(row['is_answer_absent']) >= 0.5) ):
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
            indexToken = []
            for i in oldIndexToken:
                if i not in indexToken:
                    indexToken.append(i)

            beginIndexList = []
            endIndexList = []
            for i in range(len(indexToken)):
                indexSubToken = indexToken[i].split(',')
                for k in range(len(indexSubToken)):
                    if(indexSubToken[k]!="None"):
                        index = indexSubToken[k].split(':')

                        endIndex = len(re.sub("[ ]+"," ",story_text[:int(index[1])]))
                        indexDiffer = int(index[1])-int(index[0])
                        beginIndex = endIndex-indexDiffer

                        endIndexBackup = endIndex
                        beginIndexBackup = beginIndex

                        checkList = [' ',',','.','?','!','"',"'"]
                        while(endIndex>beginIndex):
                            if(re.sub("[ ]+"," ",story_text)[endIndex-1] in checkList):
                                endIndex = endIndex-1
                            else:
                                break

                        while(beginIndex<endIndex):
                            if(re.sub("[ ]+"," ",story_text)[beginIndex] in checkList):
                                beginIndex = beginIndex+1
                            else:
                                break
                        if(beginIndex == endIndex):
                            continue
                        endIndexList.append(endIndex)
                        beginIndexList.append(beginIndex)

            newIndexToken = ""
            for i in range(len(beginIndexList)):
                if i==0:
                    newIndexToken = str(beginIndexList[i])+":"+str(endIndexList[i])
                else:
                    newIndexToken += "|"+ str(beginIndexList[i])+":"+str(endIndexList[i])


            row['answer_char_ranges'] = newIndexToken

            story_text = re.sub("[ ]+"," ",story_text)
            row['story_text'] = story_text

            answersString = ""
            for i in range(len(beginIndexList)):
                answersString += story_text[beginIndexList[i]:endIndexList[i]]+"|"
            row['is_answer_absent']=answersString


            row['story_id'] = story_id+str(docIdDic[story_id])
            writer.writerow(row)
            docIdDic[story_id] += 1

                            #			for ranges in row['answer_char_ranges'].replace(',', '|').split('|'):
                            #				if not ranges == 'None':
                            #					range_start = int(ranges.split(":")[0])
                            #					range_end = int(ranges.split(":")[1])
                            #					answer_span = story_text[range_start : range_end]

