import nltk
import pymongo
from nltk.corpus import stopwords
stopset = set(stopwords.words('english'))
 
def stopword_filter(words):
    return [word for word in words if word not in stopset]

connection = pymongo.Connection()

db = connection.debatebot

text_to_analyze = db.debate_tweets_hofstra.find().limit(1000)

text = ""

for x in text_to_analyze:
	text += x['text'].encode("utf8","ignore")

words = nltk.Text(stopword_filter(nltk.tokenize.word_tokenize(text)))

#words.collocations()

ngrams = nltk.ngrams(words, 3, pad_left=True, pad_right=True)

fdist = nltk.FreqDist(ngrams)

for k,v in fdist.items():
	if(v > 10):
		print "%s : %s \n" % (k, v)

