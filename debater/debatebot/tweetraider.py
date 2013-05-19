import tweepy
from tweepy.error import *
from datetime import datetime, tzinfo
from dateutil.tz import *
from pytz import timezone
import pytz
import pymongo
from pymongo import Connection
import time
import json

#consumer_key=
#consumer_secret = 
#access_token = 
#access_secret= 
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

def make_api():
	return tweepy.API(auth)

def search(api, **keywords):
	#function expects an authenticated api instance
	if not keywords['q']:
		raise Exception("You need to include a query, try search(api, q = 'Your Thing To Search')")
		
	x = api.search(**keywords)

	if x == []:
		raise Exception("Empty Search")
	else:
		return x
	#y.created_at = utc.localize(y.created_at)
	#print time.astimezone(tzlocal())
	#print y.created_at.astimezone(tzlocal())

def save(connection, **keywords):
	try:
		database = connection[keywords['database']]
	except:
		raise Exception("Couldn't find the database you were looking for")
	
	if database.debate_tweets_tampa.insert(keywords['tweet_object']):
		return True

def convert_to_pdt(datetime):
	utc 		= pytz.utc
	pacific 	= timezone('US/Pacific')
	datetime 	= utc.localize(datetime)
	return datetime.astimezone(pacific)

def find_shit(api, the_time_we_need, args, tweets=None, restart_id=None):
	if not tweets:
		args['max_id'] = restart_id
		tweets = search(api, **args)
	last_tweet = tweets[len(tweets)-1]
	the_late_time = convert_to_pdt(last_tweet.created_at)
	print "%s : %s" %(last_tweet.id, the_late_time.strftime('%c'))
	if the_late_time <= the_time_we_need:
		print last_tweet.id
		return True
	else:
		args['max_id'] = last_tweet.id
		try:
			tweets = search(api, **args)
		except:
			print 'borked %s' % last_tweet.id
			return False
		find_shit(api, the_time_we_need, args, tweets=tweets)

def loopy_search(q, start = None, end = None, until = None, page = None, datetime = None):
	if not start:
		start = "253749542586040320"
	if not end:
		end = "253645260029313025"
	if not page:
		page = 1
	connection = Connection()
	api = make_api()
	args = {"max_id":start, "return_type":"recent", "rpp":100, "page":page, "q":q}
	utc = pytz.utc
	print "Trying page %s..." % args['page']
	last_result = search(api, **args)
	while int(last_result.max_id) > int(end):
		for result in last_result:
			try:
				result.created_at = utc.localize(result.created_at)
			except:
				pass
			save(connection, database="debatebot", tweet_object=vars(result))
		last_id = last_result[len(last_result)-1].id
		args['page'] += 1
		print "Trying page %s..." % args['page']
		try:
			result = search(api, **args)
			print "Success!"
		except:
			args['page'] = 1
			args['max_id'] = last_id
			print "Reached last page. Starting from %s" % last_id
			try:
				result = search(api, **args)
			except TweepError:
				print "Ratelimited. Sleeping..."
				time.sleep(120)
				result = last_result
				args['page'] -= 1
				continue
		last_result = result

#close enough to midnight: 253749542586040320
#about 9:30 253714416221184001
#about 5: 253645260029313025
#  2012-10-03 19:41:51-07:00 253686339424366592
# about 7: 253676853636775936 19:04:09-07:00





# roughly 5:00pm
# 258356643396460545

# roughly midnight
# 258462051473715200

class StreamListener(tweepy.StreamListener):
    connection = Connection()
    def on_status(self, status):
        x = vars(status)
        del x['_api']
        x['author'] = status.author.screen_name
        x['user'] = status.user.id
        try:
        	x['retweeted_status'] = status.retweeted_status.id
        except:
        	pass
        print x
        save(self.connection, database='debatebot', tweet_object=x)
        #print '\n %s  %s  via %s\n' % (status.author.screen_name, status.created_at, status.source)

def kick_it():
    l = StreamListener()
    streamer = tweepy.Stream(auth=auth, listener=l, timeout=3000000000 )
    setTerms = ['#debates']
    streamer.filter(None,setTerms)
