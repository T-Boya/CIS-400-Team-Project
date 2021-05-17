"""
environment: visual studio 2019
reference: copy the function: oauth_login()
from Mining the Social Web, 3rd Edition:Chapter 9: Twitter Cookbook.
"""

import twitter
from .sentiment_analysis import create_classifier, classify_tweet
import sys
#import networkx as nx
#import matplotlib.pyplot as plt


def oauth_login():
    '''
    Creates logged-in twitter API oauth object
    '''    
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

    # Create some variables to store data
    tweet_Max = numberOfTweet
    tweet_Counter = 0
    list_Of_Tweets = []
    list_Of_Weights = []

    # Set up stream
    twitter_api = oauth_login()
    twitter_stream = twitter.TwitterStream(auth=twitter_api.auth)
    print('Filtering the public timeline for track = {0}'.format(listOfTerms), file=sys.stderr)
    sys.stderr.flush()

    # Attempt to collect 100 politically relevant tweets from stream
    try:
        stream = twitter_stream.statuses.filter(track=listOfTerms)
        for tweet in stream:
            try:
                # Create list of tweet bodies and list of weights using community detection algorithm
                list_Of_Tweets.append(tweet['text'])
                list_Of_Weights.append(max(1, int(round(int(tweet['retweet_count']) * 0.4 + int(tweet['favorite_count']) * 0.2))))

                # Stop collecting tweets once desired number has been reached
                tweet_Counter += 1
                if tweet_Counter == tweet_Max:
                    break

            # Handle error
            except:
                return True, 0, 0

    # Handle error if rate limiting is occurring
    except:
        return True, 0, 0

    # Run sentiment analysis on tweets
    sys.stdout.flush()
    classifier, vect = create_classifier()
    tot = len(list_Of_Tweets)
    i = 0
    correct_dem = 0
    correct_rep = 0
    ef = classify_tweet(classifier, vect, list_Of_Tweets)

    # Print statements to show progress in console
    print(ef)
    print(str(len(list_Of_Tweets)), "tweets")
    print(str(len(ef)), "analyzed")

    # Prepare data for webpage
    for i in range(len(ef)):
        if ef[i] == "Democrat":
                correct_dem += list_Of_Weights[i]
        if ef[i] == "Republican":
                correct_rep += list_Of_Weights[i]
        i += 1

    return False, correct_dem, correct_rep