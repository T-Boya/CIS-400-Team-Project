import csv
from django.contrib.staticfiles.finders import find
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import HashingVectorizer


def pullTestData(dem_tweets, rep_tweets):
    n = 2000
    ans = []
    with open('ExtractedTweets.csv', 'r', newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile)
        d = 0
        r = 0
        for row in reader:
            if row[0] == 'Democrat' and d < n/2:
                dem_tweets.append(row[2])
                ans.append(row[0])
                d += 1
            elif row[0] == 'Republican' and r < n/2:
                rep_tweets.append(row[2])
                ans.append(row[0])
                r += 1
            if d + r >= n:
                break
        csvfile.close()
        return ans


def big_training():
    clf = MultinomialNB()
    with open(find('CSV/ExtractedTweets.csv'), 'r', newline='', encoding="utf8") as csvfile:
        first = True
        word_features = []
        dem_tweets = [("Democrat", "Trump Sucks")]
        rep_tweets = [("Republican", "Biden Sucks")]
        b = 0
        while dem_tweets != [] or rep_tweets != []:
            print("Training pass starting, b: " + str(b))
            reader = csv.reader(csvfile)
            dem_tweets, rep_tweets, reader, key = pullSomeTestData(3000, reader)
            if dem_tweets == [] and rep_tweets == []:
                break
            b += 3000
            vectorizer = HashingVectorizer(stop_words='english', alternate_sign=False)
            tweets = vectorizer.transform(dem_tweets+rep_tweets)
            clf.partial_fit(tweets, key, classes=["Democrat","Republican"], sample_weight=1)
            #word_features = word_features + get_word_features(get_words_in_tweets(tweets))
            #training_set = [(extract_features(d, word_features), c) for (d, c) in tweets]
            """
            if first:
                cs = NaiveBayesClassifier.train(training_set)
                first = False
            else:
                cs = cs.train(training_set)
            """
        return clf #, word_features


def pullSomeTestData(n, reader):
    i = 0
    d_tweets = []
    r_tweets = []
    key = []
    while i < n:
        try:
            t = reader.__next__()
            if t[0] == 'Democrat':
                d_tweets.append(t[2])
                key.append(t[0])
            elif t[0] == 'Republican':
                r_tweets.append(t[2])
                key.append(t[0])
            i += 1
        except csv.Error:
            print("Error")
            break
        except StopIteration:
            print("Iteration End")
            break
    return d_tweets, r_tweets, reader, key

def create_classifier():
    vectorizer = HashingVectorizer(stop_words='english', alternate_sign=False)
    classifier = big_training()
    return classifier, vectorizer


def classify_tweet(cs, vect, tweets):
    return cs.predict(vect.transform(tweets))

def classify_tweets_count(cs, vect, tweets):
    ef = cs.predict(vect.transform(tweets))
    dem = 0
    rep = 0
    for g in ef:
        if g == "Democrat":
            dem += 1
        else:
            rep += 1
    return dem, rep