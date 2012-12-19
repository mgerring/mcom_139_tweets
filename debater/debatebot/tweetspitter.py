from datetime import datetime, timedelta
from pytz import timezone
import pytz
import pymongo
from pymongo import Connection
import codecs

utc 		= pytz.utc
pacific 	= timezone('US/Pacific')
connection 	= Connection()
db 			= connection.debatebot
new_file 	= codecs.open('tweet_sample_tampa.txt', 'w', 'utf-8')
tweet_ids	= []


#get the tweets from the db. iterate over them, write to a file one at a time, and presto!

gte 	= datetime(2012, 10, 22, 17, 00, 00, tzinfo=pacific) #5:00
lte 	= gte + timedelta(minutes = 10)
final	= datetime(2012, 10, 23, 00, 00, 00, tzinfo=pacific) #midnight

while final.strftime("%s") > gte.strftime("%s"):
	help_text = "From %s to %s:" % ( gte.strftime("%c"), lte.strftime("%c") )
	print help_text
	new_file.write( help_text )
	tweet_block = db.debate_tweets_tampa.find({'created_at':{'$gte':gte, '$lte':lte}}).limit(20)
	for tweet in tweet_block:
		if tweet['id'] not in tweet_ids: 
			tweet_ids.append(tweet['id'])
			print "writing tweet"
			new_file.write( utc.localize(tweet['created_at']).astimezone(pacific).strftime("%c") )
			new_file.write("\n")
			new_file.write("@%s" % tweet['author'])
			new_file.write("\n")
			new_file.write(tweet['text'])
			new_file.write("\n\n")
		else:
			print "skipped"
	gte = lte
	lte += timedelta(minutes = 2)