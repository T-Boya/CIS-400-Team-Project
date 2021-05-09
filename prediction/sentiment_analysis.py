from textblob import TextBlob
import csv
from nltk import *
from django.contrib.staticfiles.storage import staticfiles_storage

test_tweet_questions = []
test_tweet_answers = []


def pullTestData(dem_tweets, rep_tweets):
    n = 10000
    tn = 1000
    with open(staticfiles_storage.url('CSV/ExtractedTweets.csv'), 'r', newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile)
        rdem_tweets = []
        rrep_tweets = []
        d = 0
        r = 0
        i = 0
        while i < 3000:
            next(reader)
            i += 1
        for row in reader:
            if row[0] == 'Democrat' and d < n/2:
                dem_tweets.append((row[2], row[0]))
                rdem_tweets.append(row)
                d += 1
            elif row[0] == 'Republican' and r < n/2:
                rep_tweets.append((row[2], row[0]))
                rrep_tweets.append(row)
                r += 1
            elif row[0] == 'Democrat' and n / 2 <= d < n / 2 + tn / 2:
                test_tweet_questions.append(row[2])
                test_tweet_answers.append(row[0])
                d += 1
            elif row[0] == 'Republican' and n / 2 <= r < n / 2 + tn / 2:
                test_tweet_questions.append(row[2])
                test_tweet_answers.append(row[0])
                r += 1
            if d + r >= n + tn:
                break
        csvfile.close()


def train(dem_tweets, rep_tweets, tweets):
    for (words, sentiment) in dem_tweets + rep_tweets:
        words_filtered = [e.lower() for e in words.split() if len(e) >= 3]
        tweets.append((words_filtered, sentiment))


def get_words_in_tweets(tweets):
    all_words = []
    for (words, sentiment) in tweets:
        all_words += words
    return all_words


def get_word_features(wordlist):
    wordlist = FreqDist(wordlist)
    # word_features = wordlist.keys() # careful here
    word_features = [w for (w, c) in wordlist.most_common(1750)] #use most_common() if you want to select the most frequent words
    return word_features


# print  word_features

def extract_features(document, word_features):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features


def create_classifier():
    dem_tweets = [("Democrat", "Trump Sucks")]
    rep_tweets = [("Republican", "Biden Sucks")]
    tweets = []
    pullTestData(dem_tweets, rep_tweets)
    train(dem_tweets, rep_tweets, tweets)
    word_features = get_word_features(get_words_in_tweets(tweets))
    training_set = [(extract_features(d, word_features), c) for (d, c) in tweets]
    classifier = NaiveBayesClassifier.train(training_set)
    return classifier, word_features


def classify_tweet(cs, wf2, tweet):
    return cs.classify(extract_features([e.lower() for e in tweet.split() if len(e) >= 3], wf2))


if __name__ == "__main__":
    """"
    myAuth = twitter.oauth.OAuth(consumer_key='cvUnT3e5uMm7URiYZscsED8DF',  # just auth stuff
                                 consumer_secret='IfFSYmujlz2F3HlKQk8mZ6sgZc10646pniF2Utvd8lEx4l1Ckg',
                                 token='980873561886937088-jgzxBfvmibqClm8twVLzqFiUBHvK4ua',
                                 token_secret='QNTPfO6UKO92t6ECZb2o8L9Dig2uYtSn2OSi5ApOuqQSC')
    tw = twitter.Twitter(auth=myAuth)
    s = tw.search.tweets(q="Biden", tweet_mode='extended', count="100", include_entities="false", result_type="mixed", lang="en")
    test_tweets = []
    for t in s["statuses"]:
        test_tweets.append(t["full_text"])
    pullTestData()
    train()
    training_set = [(extract_features(d), c) for (d, c) in tweets]
    classifier = NaiveBayesClassifier.train(training_set)
    """

    # YOU NEED THIS NEXT LINE
    classifier, wf = create_classifier()
    tot = len(test_tweet_questions)
    i = 0
    correct_dem = 0
    correct_rep = 0
    while i < tot:
        ef = classify_tweet(classifier, wf, test_tweet_questions[i])
        print(ef + " : " + test_tweet_answers[i])
        if ef == test_tweet_answers[i]:
            if test_tweet_answers[i] == "Democrat":
                correct_dem += 1
            else:
                correct_rep += 1
        i += 1
    print("Correctness: " + str((correct_dem + correct_rep)/tot))
    print("Dem correctness: " + str(correct_dem/(tot/2)))
    print("Rep correctness: " + str(correct_rep/(tot/2)))
    #for t in test_tweets:
         #print "{0} : {1}".format(t, classifier.classify(extract_features(t.split())))
        #print(
            #"{0} : {1}".format(t, classifier.classify(extract_features([e.lower() for e in t.split() if len(e) >= 3]))))s