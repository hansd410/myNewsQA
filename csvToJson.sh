#python2 required
python preprocess.py data/newsqa/train.csv data/preprocess/train_preprocessed.csv
python preprocess.py data/newsqa/dev.csv data/preprocess/dev_preprocessed.csv
python preprocess.py data/newsqa/test.csv data/preprocess/test_preprocessed.csv

python toJson.py data/preprocess/train_processed.csv data/toJson/train.json
python toJson.py data/preprocess/dev_processed.csv data/toJson/dev.json
python toJson.py data/preprocess/test_processed.csv data/toJson/test.json

python answerReposition.py data/toJson/train.json data/result/train.json
python answerReposition.py data/toJson/dev.json data/result/dev.json
python answerReposition.py data/toJson/test.json data/result/test.json

