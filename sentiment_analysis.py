import csv
from nltk.corpus import stopwords
from nltk import *
from nltk import word_tokenize
import pickle
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
    with open('ExtractedTweets.csv', 'r', newline='', encoding="utf8") as csvfile:
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


def train(dem_tweets, rep_tweets):
    tweets = []
    stop_words = set(stopwords.words('english'))
    for (words, sentiment) in dem_tweets + rep_tweets:
        words_filtered = [e.lower() for e in words.split() if len(e) >= 3 and not e in stop_words]
        tweets.append((words_filtered, sentiment))
    return tweets


def get_words_in_tweets(tweets):
    all_words = []
    for (words, sentiment) in tweets:
        all_words += words
    return all_words


def get_word_features(wordlist):
    wordlist = FreqDist(wordlist)
    # word_features = wordlist.keys() # careful here
    word_features = [w for (w, c) in wordlist.most_common(1100)] #use most_common() if you want to select the most frequent words
    return word_features


# print  word_features

def extract_features(document, word_features):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features


def create_classifier():
    vectorizer = HashingVectorizer(stop_words='english', alternate_sign=False)
    try:
        classifier = pickle.load(open("trained_classifier", "rb"))
    except OSError as e:
        print(e)
        classifier = big_training()
        pickle.dump(classifier, open("trained_classifier", "wb"))
    return classifier, vectorizer


def classify_tweets(cs, vect, tweets):
    return cs.predict(vect.transform(tweets))


if __name__ == "__main__":
    tqr = [""]
    tqd = [""]
    ans = pullTestData(tqr, tqd)
    classifier, vectorizer = create_classifier()
    #test_tweet_questions = vectorizer.transform(tqr + tqd)
    test_tweet_questions = tqr + tqd
    ef = classify_tweets(classifier, vectorizer, test_tweet_questions)
    correct_dem = 0
    correct_rep = 0
    tot = 2000
    for g, a in zip(ef, ans):
        if g == a and a == "Democrat":
            correct_dem += 1
        elif g == a:
            correct_rep += 1
    print("Correctness: " + str((correct_dem + correct_rep)/tot))
    print("Dem correctness: " + str(correct_dem/(tot/2)))
    print("Rep correctness: " + str(correct_rep/(tot/2)))