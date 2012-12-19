from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import pymongo
import json
from bson import BSON
from bson import json_util
from dateutil.parser import parse as strtotime
import nltk
from nltk.collocations import *
from nltk.corpus import stopwords
import re
import itertools
import math
from nltk.stem.wordnet import WordNetLemmatizer

connection = pymongo.Connection()
db = connection.debatebot

stopset = set(stopwords.words('english') + ['debate','debates','rt'])
atnames = re.compile('(?<=^|(?<=[^a-zA-Z0-9-_\\.]))(@[A-Za-z]+[A-Za-z0-9]+)')
hashtags = re.compile('(?<=^|(?<=[^a-zA-Z0-9-_\\.]))(#[A-Za-z]+[A-Za-z0-9]+)')
#rt = re.compile('((RT|rt):?)')
#links = re.compile(r"(^|[\n ])(([\w]+?://[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)
links = "(^|[\n ])(([\w]+?://[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)"
punct = re.compile('&amp|[!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~+]')
#punct_no_hastags = re.compile('&amp|[!"$%&\'()*+,-./:;<=>?[\\]^_`{|}~+]|[@#](?![A-Za-z]+[A-Za-z0-9]+)')
punct_no_hastags = '(&amp|[!"$%&\'()*+,-./:;<=>?[\\]^_`{|}~+]|[@#](?![A-Za-z]+[A-Za-z0-9]+))'
twitter = re.compile('(%s|%s)'%(links,punct_no_hastags))


def home(request):
	return render_to_response('main.html', context_instance=RequestContext(request) )

def get(request, collection = None, limit = None):
	if connection:
		tweets = db[collection].find()

	if limit:
		tweets.limit(int(limit))

	data = [result for result in tweets]
	return_json = json.dumps(data, default=json_util.default)

	return HttpResponse(return_json,mimetype='application/json')

def rate(request, collection = None, limit = None):
	
	if connection:
		tweets = db[collection].find()

	if limit:
		tweets.limit(int(limit))

	data = [result for result in tweets]
	return_json = json.dumps(data, default=json_util.default)

	return HttpResponse(return_json,mimetype='application/json')

def words(request, collection = None, begin = 0, end = 0, limit = 100):
	filters = {}
	min_time = db.tweet_meta.find_one({'collection':collection,'key':'min_date'})['value']
	max_time = db.tweet_meta.find_one({'collection':collection,'key':'max_date'})['value']

	begin = int(begin)
	end = int(end)
	limit = int(limit)

	if not begin:
		begin = min_time
	else:
		begin = datetime.fromtimestamp( begin )

	if not end:
		end = max_time
	else:
		end = datetime.fromtimestamp( end )

	filters['created_at'] = {
		'$gte' : begin,
		'$lte' : end,
	}

	results = _word_and_bigram_fd([result for result in db[collection].find(filters).limit(2000)])

	return_val = {}
	return_val['min_time'] = min_time.strftime('%s')
	return_val['max_time'] = max_time.strftime('%s')
	return_val['high'] = results[0][0][1]
	return_val['low'] = results[0][len(results[0])-1][1]
	return_val['low'] = return_val['low'] if return_val['low'] > 0 else 1
	return_val['words'] = results
	return_json = json.dumps(return_val, default=json_util.default)
	return HttpResponse(return_json,mimetype='application/json')

def _obama_romney_filter(text):
	return_words = []
	obama = 0
	romney = 0
	for word in text:
		if word in "mitts romneys":
			romney+=1
		elif word in "baracks obamas":
			obama+=1
		else:
			return_words.append(word)
	return (return_words, obama, romney)

def _word_filter(text):
	return [word for word in text if word not in stopset and word != "" and len(word) > 2]

def _twitter_filter(text):
	text = twitter.sub('', text)
	return text

def _word_and_bigram_fd(tweets):
	lmtzr = WordNetLemmatizer()
	text = ""

	for tweet in tweets:
		text += tweet['text'].encode("utf8","ignore").lower()

	text = _twitter_filter(text)

	hashtag_fd = hashtags.findall(text)
	text = hashtags.sub("",text)

	atname_fd = atnames.findall(text)
	text = atnames.sub("",text)

	text = text.split(" ")
	text = _word_filter(text)
	text, obama, romney = _obama_romney_filter(text)
	text = [lmtzr.lemmatize(word) for word in text]

	bigram_measures = nltk.collocations.BigramAssocMeasures()

	# change this to read in your data
	finder = BigramCollocationFinder.from_words(text)
	# only bigrams that appear 3+ times
	finder.apply_freq_filter(3)

	word_fd = finder.word_fd.items()[:100]
	bigram_fd = finder.ngram_fd.items()[:100]

	for w_index, word in enumerate(word_fd):
		for b_index, bigram in enumerate(bigram_fd):
			if word[0] in bigram[0]:
				word_fd[w_index] = (word[0], math.fabs(word[1]-bigram[1]))

	bigram_fd = [(' '.join(str(i) for i in b[0]), b[1]) for b in bigram_fd]

	data = [x for x in itertools.chain( word_fd, bigram_fd ) ]
	data.sort(key=lambda tup: tup[1])
	data.reverse()
	return ( data[:100], nltk.FreqDist(atname_fd).items(), nltk.FreqDist(hashtag_fd).items(), obama, romney)