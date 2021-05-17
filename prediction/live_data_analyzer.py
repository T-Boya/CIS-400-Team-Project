"""
environment: visual studio 2019
reference: copy the function: oauth_login()
from Mining the Social Web, 3rd Edition:Chapter 9: Twitter Cookbook.
"""

import twitter
from textblob import TextBlob
import json, time
from urllib.error import URLError
from http.client import BadStatusLine
from .sentiment_analysis import create_classifier, classify_tweet
import sys
#import networkx as nx
#import matplotlib.pyplot as plt


def oauth_login():
    # XXX: Go to http://twitter.com/apps/new to create an app and get values
    # for these credentials that you'll need to provide in place of these
    # empty string values that are defined as placeholders.
    # See https://developer.twitter.com/en/docs/basics/authentication/overview/oauth
    # for more information on Twitter's OAuth implementation.
    
    CONSUMER_KEY = 'KmtQre6nXaxlhrov6b98zoo3W'
    CONSUMER_SECRET = 'YQBO45L8IkuOeHJSwWtchOlVjzJBDkQwOZoZMgLzg4TN0NV8Ft'
    OAUTH_TOKEN = '1366839526208004101-Hjs0iSxyWGzbrLoc3BFU6KDF2oX4DE'
    OAUTH_TOKEN_SECRET = '6rkguLQR4BtOkLyhYXNtxNvUVyZ5XqjbFeXR7QnJKNxp2'
    
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET)
    
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

#Using twitter stream timeline to find the current tweet with filtered terms. 
#Tweet will be sentiment analysis. 
#Return a list of all positive sentiment tweet ID and negative sentiment tweet ID.
def Current_Tweets_Sentiment(listOfTerms, numberOfTweet):
    # Returns an instance of twitter.Twitter
    twitter_api = oauth_login()

    # Reference the self.auth parameter
    # ADD FUNCTION WRAPPER FOR API RATE LIMITS!
    twitter_stream = twitter.TwitterStream(auth=twitter_api.auth)

    #posTweetID = []
    #negTweetID = []
    tweet_Max = numberOfTweet
    tweet_Counter = 0
    list_Of_Tweets = []
    list_Of_Weights = []
    dem_tweets = []
    rep_tweets = []

    print('Filtering the public timeline for track = {0}'.format(listOfTerms), file=sys.stderr)
    sys.stderr.flush()

    stream = twitter_stream.statuses.filter(track=listOfTerms)

    #Uncomment if want to write to file.
    #f = open(listOfTerms+".txt", 'w');
    for tweet in stream:
        max_errors = 10
        try:

            """
            #print and write to file
            print (tweet['id'])
            print (tweet['text'])
            #Save to a database in a particular collection
            json.dump(tweet['id'], f, indent=1, sort_keys=True)
            f.write("\n")
            json.dump(tweet['text'], f, indent=1, sort_keys=True)       
            f.write("\n\n")
            """

            """
            #Bad Sentiment analysis
            #sentiment analysis using TextBlob
            blob = TextBlob(tweet['text'])
            sentimentScore = 0
            for sentence in blob.sentences:
                sentimentScore += sentence.sentiment.polarity
            #print(sentimentScore)
            #adding id to positive or negative tweet list
            if sentimentScore > 0:
                posTweetID.append(tweet['id'])
            if sentimentScore < 0:
                negTweetID.append(tweet['id'])
            """
            # print('NEW TWEET:')
            # print(tweet)
            # print("WEIGHT: ", end = '')
            # print(min(1, str(int(tweet['retweet_count']) * 0.4 + int(tweet['favorite_count']) * 0.2)))
            # print('\n\n')

            #Making a list of all tweets and weights
            if 'limit' in tweet:
                print(tweet)
                print('sleeping for 2 mins')
                time.sleep(60 * 2 + 5)
                continue

            list_Of_Tweets.append(tweet['text'])
            list_Of_Weights.append(max(1, int(round(int(tweet['retweet_count']) * 0.4 + int(tweet['favorite_count']) * 0.2))))

            #get a number of tweet in stream
            tweet_Counter += 1
            if tweet_Counter == tweet_Max:
                break

        except:
            return True, 0, 0

    """
    #write positive and negative to file
    f.write('POSITIVE TWEET ID \n')
    json.dump(posTweetID, f, indent=1, sort_keys=True)
    f.write('\n\n')
    f.write('NEGATIVE TWEET ID \n')
    json.dump(negTweetID, f, indent=1, sort_keys=True)
    f.write('\n\n')
    """
    #Uncomment if want to write to file.
    #f.close()
    sys.stdout.flush()

    #New Sentiment analysis on listOfTweets
    classifier, vect = create_classifier()
    tot = len(list_Of_Tweets)
    i = 0
    correct_dem = 0
    correct_rep = 0
    ef = classify_tweet(classifier, vect, list_Of_Tweets)
    print(ef)
    print(str(len(list_Of_Tweets)), "tweets")
    print(str(len(ef)), "analyzed")
    for i in range(len(ef)):
        # print(list_Of_Tweets[i])
        if ef[i] == "Democrat":
                correct_dem += list_Of_Weights[i]
        if ef[i] == "Republican":
                correct_rep += list_Of_Weights[i]
        i += 1

    return False, correct_dem, correct_rep

