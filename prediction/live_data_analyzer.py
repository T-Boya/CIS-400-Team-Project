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

from twitter.api import TwitterHTTPError
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

def Current_Tweets_Sentiment(listOfTerms, numberOfTweet):
    '''
    Use twitter streaming API  to fetch 100 politically-relevant tweets 
    and analyze their political affiliation
    Outputs the number of democratic and republican tweets
    '''

    tweet_Max = numberOfTweet
    tweet_Counter = 0
    list_Of_Tweets = []
    list_Of_Weights = []

    # Returns an instance of twitter.Twitter
    twitter_api = oauth_login()
    # Reference the self.auth parameter
    twitter_stream = twitter.TwitterStream(auth=twitter_api.auth)

    print('Filtering the public timeline for track = {0}'.format(listOfTerms), file=sys.stderr)
    sys.stderr.flush()

    try:
        stream = twitter_stream.statuses.filter(track=listOfTerms)
        for tweet in stream:
            max_errors = 10
            try:

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
    except:
        return True, 0, 0

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
        if ef[i] == "Democrat":
                correct_dem += list_Of_Weights[i]
        if ef[i] == "Republican":
                correct_rep += list_Of_Weights[i]
        i += 1

    return False, correct_dem, correct_rep