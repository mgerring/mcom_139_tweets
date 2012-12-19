import pymongo

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