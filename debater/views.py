# -*- coding: utf-8 -*-
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
import nltk
from nltk.collocations import *
from nltk.corpus import stopwords
import re
import itertools
import math
from nltk.stem.wordnet import WordNetLemmatizer
import StringIO
import csv

connection = pymongo.Connection()
db = connection.debatebot
atnames = re.compile('(?<=^|(?<=[^a-zA-Z0-9-_\\.]))(@[A-Za-z]+[A-Za-z0-9]+)')
hashtags = re.compile('(?<=^|(?<=[^a-zA-Z0-9-_\\.]))(#[A-Za-z]+[A-Za-z0-9]+)')
links = "(^|[\n ])(([\w]+?://[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)"
numbers = re.compile('(\d|[.,+])+')
errant_rt = re.compile('(rt$)')
#punct = re.compile('&amp|[!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~+]')
#punct_no_hastags = '(&amp|[!"$%&\'()*+,-./:;<=>?[\\]^_`{|}~+]|[@#](?![A-Za-z]+[A-Za-z0-9]+))'
#twitter = re.compile('(%s|%s)'%(links,punct_no_hastags))
twitter = re.compile(links)

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
	return_val = get_the_words(collection = collection, begin = begin, end = end, limit = limit)
	return_json = json.dumps(return_val, default=json_util.default)
	return HttpResponse(return_json,mimetype='application/json')

def to_csv(request, collection = None, begin = 0, end = 0, limit = 100):
	return_val = get_the_words(collection = collection, begin = begin, end = end, limit = limit)
	to_csv = return_val['words'][0] + return_val['words'][1] + return_val['words'][2] + return_val['words'][3]
	outfile = StringIO.StringIO()
	writer = csv.writer(outfile, dialect="excel")
	for val in to_csv:
		writer.writerow(val)
	outfile.seek(0)
	response = HttpResponse(outfile.read(),mimetype='text/csv')
	response['Content-Disposition'] = 'attachment; filename=thing.csv'
	return response

def get_time_bounds(collection = None):
	min_time = db.tweet_meta.find_one({'collection':collection,'key':'min_date'})['value']
	max_time = db.tweet_meta.find_one({'collection':collection,'key':'max_date'})['value']
	return (min_time,max_time)

def get_from_db(collection,begin,end,filters = None):
	if filters == None:
		filters = {}
	filters['created_at'] = {
		'$gte' : begin,
		'$lte' : end,
	}
	return _word_and_bigram_fd([result for result in db[collection].find(filters).limit(2000)])

def get_the_words(collection = None, begin = 0, end = 0, limit = 100):
	filters = {}
	# Find the start and end times of tweets in the database.
	# Tweets are (should be) indexed on min and max date.
	#
	# TODO: Backup Mongo database, figure out a way to authoritatively
	# mark the date field for indexing.

	min_time, max_time = get_time_bounds(collection = collection)

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

	results = get_from_db(collection,begin,end,filters)

	return_val = {}
	return_val['min_time'] = min_time.strftime('%s')
	return_val['max_time'] = max_time.strftime('%s')
	return_val['words'] = results
	return return_val

def _obama_romney_filter(text):
	return_words = []
	obama = 0
	romney = 0
	for word in text:
		if word in "mitts romneys mitt's romney's":
			romney+=1
		elif word in "baracks obamas barrys barack's obama's barry's":
			obama+=1
		else:
			return_words.append(word)
	return (return_words, obama, romney)

def _punct_filter(text):
	return [word.strip('“":.;?-&,!\'()_/\\') for word in text]

def _word_filter(text):
	stopset = set(stopwords.words('english') + ['debate','debates','#debates','rt','2nd','1st','amp',"abc","you'll","i'm"])
	return [word for word in text if word not in stopset and word != "" and len(word) > 2]

def _twitter_filter(text):
	text = twitter.sub('', text)
	return text

def _word_and_bigram_fd(tweets):
	lmtzr = WordNetLemmatizer()
	text = ""

	for tweet in tweets:
		text += tweet['text'].encode("utf8","replace").lower()
		text += " "

	hashtag_fd = [word for word in hashtags.findall(text)]
	text = hashtags.sub("",text)

	atname_fd = [word for word in atnames.findall(text)]
	text = atnames.sub("",text)

	text = _twitter_filter(text)

	text = numbers.sub("",text)

	text = text.split(" ")
	text = _punct_filter(text)
	text = _word_filter(text)
	text, obama, romney = _obama_romney_filter(text)
	text = [lmtzr.lemmatize(word) for word in text]

	bigram_measures = nltk.collocations.BigramAssocMeasures()

	# change this to read in your data
	finder = BigramCollocationFinder.from_words(text)
	# only bigrams that appear 3+ times
	finder.apply_freq_filter(3)

	word_fd = finder.word_fd.items()[:100]
	#bigram_fd = finder.ngram_fd.items()[:100]
	#bigram_fd = [(' '.join(str(i) for i in b[0]), b[1]) for b in bigram_fd]
	#final_fd = {}

	"""for bigram in bigram_fd: #check every bigram
		for word in word_fd: #for every word,
			if word[0] in bigram[0]: #if the word is in the bigram,
				#add the greater of the two. Assign the absolute value of the
				#difference to the smaller.

				temp = [word,bigram]
				temp.sort(key=lambda x: x[1])
				final_fd[ temp[0][0] ] = temp[0]
				final_fd[ temp[1][0] ] = ( temp[1][0], math.fabs( temp[0][1] - temp[1][1] ) )
	"""
	#final_fd = final_fd.values() 
	word_fd.sort( key=lambda tup: tup[1] )
	word_fd.reverse()
	return ( word_fd, nltk.FreqDist(atname_fd).items(), nltk.FreqDist(hashtag_fd).items(), [('Obama',obama), ('Romney',romney)] )
