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


def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):
    
        if wait_period > 3600: # Seconds
            print('Too many retries. Quitting.', file=sys.stderr)
            raise e
    
        # See https://developer.twitter.com/en/docs/basics/response-codes
        # for common codes
    
        if e.e.code == 401:
            print('Encountered 401 Error (Not Authorized)', file=sys.stderr)
            return None
        elif e.e.code == 404:
            print('Encountered 404 Error (Not Found)', file=sys.stderr)
            return None
        elif e.e.code == 429: 
            print('Encountered 429 Error (Rate Limit Exceeded)', file=sys.stderr)
            if sleep_when_rate_limited:
                print("Retrying in 15 minutes...ZzZ...", file=sys.stderr)
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print('...ZzZ...Awake now and trying again.', file=sys.stderr)
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print('Encountered {0} Error. Retrying in {1} seconds'                  .format(e.e.code, wait_period), file=sys.stderr)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e

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
                print('sleeping for 5 mins')
                time.sleep(60 * 5 + 5)
                continue

            list_Of_Tweets.append(tweet['text'])
            list_Of_Weights.append(max(1, int(round(int(tweet['retweet_count']) * 0.4 + int(tweet['favorite_count']) * 0.2))))

            #get a number of tweet in stream
            tweet_Counter += 1
            if tweet_Counter == tweet_Max:
                break

        except twitter.api.TwitterHTTPError:
            print('API ERROR TYPE {}'.format('HTTP ERROR'))
            error_count = 0 
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        
        except URLError as e:
            print('API ERROR TYPE {}'.format('URL ERROR'))
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print("URLError encountered. Continuing.", file=sys.stderr)
            if error_count > max_errors:
                print("Too many consecutive errors...bailing out.", file=sys.stderr)
                raise

        except BadStatusLine as e:
            print('API ERROR TYPE {}'.format('STATUS ERROR'))
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print("BadStatusLine encountered. Continuing.", file=sys.stderr)
            if error_count > max_errors:
                print("Too many consecutive errors...bailing out.", file=sys.stderr)
                raise

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
    classifier, wf = create_classifier()
    tot = len(list_Of_Tweets)
    i = 0
    correct_dem = 0
    correct_rep = 0
    while i < tot:
        # print(list_Of_Tweets[i])
        ef = classify_tweet(classifier, wf, list_Of_Tweets[i])
        if ef == "Democrat":
                dem_tweets.append(list_Of_Tweets[i])
                correct_dem += list_Of_Weights[i]
        if ef == "Republican":
                correct_rep += list_Of_Weights[i]
                rep_tweets.append(list_Of_Tweets[i])
        i += 1

    return correct_dem, dem_tweets, correct_rep, rep_tweets