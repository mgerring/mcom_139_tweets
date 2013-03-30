import pymongo
from debater import views as v
from datetime import timedelta
import time
from collections import Counter
import json
import os

def build_indexes(db, collections):
	db = pymongo.Connection()[db]
	db.debate_tweets_hofstra.create_index('created_at',1,unique=False)

def build_db(db,collections=None):
	db = pymongo.Connection()[db]

	if not collections:
		return False

	for collection in collections:
		date_sorted = db[collection].find().sort('created_at',1)
		first = date_sorted[0]['created_at']
		last = date_sorted[date_sorted.count()-1]['created_at']
		db.tweet_meta.save({'collection':collection,'key':'min_date','value':first})
		db.tweet_meta.save({'collection':collection,'key':'max_date','value':last})

def build_wordcount(db,collection=None):
	db = pymongo.Connection()[db]
	word_counts = pymongo.Connection()['word_counts']
	min_time, max_time = v.get_time_bounds(collection = collection)

	start 	= min_time
	end 	= min_time + timedelta(minutes=2)
	
	while time.mktime(end.timetuple()) <= time.mktime(max_time.timetuple()):
		results = v.get_from_db(collection,start,end)

		for i1, result in enumerate(results):
			for i2, x in enumerate(result):
				results[i1][i2] = (x[0].decode('utf-8','replace'), x[1])
		
		if word_counts[collection].insert({'timestamp':start, 'results':results}):
			print 'O DANG'

		start = end
		
		if time.mktime(end.timetuple()) == time.mktime(max_time.timetuple()):
			break

		end = end + timedelta(minutes=2)

		if time.mktime(end.timetuple()) > time.mktime(max_time.timetuple()):
			end = max_time

def build_choosetwo(collection=None):
	db = pymongo.Connection()['word_counts']
	word_counts = pymongo.Connection()['word_counts']
	min_time, max_time = v.get_time_bounds(collection = collection)
	start = min_time

	while start < max_time:

		timestamps = [start]

		data = [Counter(),Counter(),Counter(),Counter()]

		while max_time not in timestamps:
			
			data = aggregate_and_save(db, collection, timestamps, data)

			new_stamp = timestamps[ len(timestamps) - 1 ] + timedelta( minutes=2 )

			if new_stamp > max_time:
				break

			timestamps.append( new_stamp )

		start += timedelta( minutes=2 )

def aggregate(db, collection, timestamps, data):
	report = db[collection].find_one( { 'timestamp':timestamps[ len(timestamps)-1 ] } )

	for i, dimension in enumerate(report['results']):
		data[i] += Counter({x[0]:x[1] for x in dimension})

	return data

def save_json(collection, timestamps, results):

	save_dir = 'json/%s' % collection

	if not os.path.exists(save_dir):
		os.makedirs(save_dir)

	data_to_save = []

	for result in results:
		data_to_save.append( result.most_common(100) )

	f = open('%s/%s-%s.json' % ( save_dir, int(time.mktime(timestamps[0].timetuple())), int(time.mktime(timestamps[ len(timestamps) - 1 ].timetuple()) )), 'w')
	f.write( json.dumps( data_to_save ) )

def aggregate_and_save(db, collection, timestamps, data):
	results = aggregate(db, collection, timestamps, data)
	save_json( collection, timestamps,  results)
	return results

def build_meta_json(collection):
	c = pymongo.Connection().word_counts
	d = c[collection].find()
	f = [ e['timestamp'].strftime('%s') for e in d]
	g = open('debater/static/json/%s/%s_meta.json' % (collection, collection), 'w')
	g.write(json.dumps(f))
	g.close()
