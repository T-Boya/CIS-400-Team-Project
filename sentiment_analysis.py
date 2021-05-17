import csv
from nltk.corpus import stopwords
from nltk import *
from nltk import word_tokenize
import pickle
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import HashingVectorizer


# this function pulls 2000 tweets, half republican, and half democrat from our test data file.
# it puts the data into the given arguments
# it returns the classifications of each tweet in order
# because our dataset has all demcrat tweets before any republican we don' need to keep track of the order of our answers
# we just put all demcrat tweets before all the republican tweets
def pullTestData(dem_tweets, rep_tweets):
    n = 2000
    ans = []
    with open('ExtractedTweets.csv', 'r', newline='', encoding="utf8") as csvfile: # open the file
        reader = csv.reader(csvfile) # create a reader
        d = 0 # vars to store the number of reps and dems found so far
        r = 0
        for row in reader: # if the row starts with "Democrat" then we mark it as a dem
            if row[0] == 'Democrat' and d < n/2:
                dem_tweets.append(row[2])
                ans.append(row[0])
                d += 1
            elif row[0] == 'Republican' and r < n/2: # if not then it must be a republican
                rep_tweets.append(row[2])
                ans.append(row[0])
                r += 1
            if d + r >= n: # when we have enough of each tweet type then we stop
                break
        csvfile.close()
        return ans

# Train our classifier on all 85K tweets in our dataset
# returns the classifier
def big_training():
    clf = MultinomialNB() # create an untrained classifier.
    vectorizer = HashingVectorizer(stop_words='english', alternate_sign=False) # create our vectorizer to turn tweets into matrixes
    with open('ExtractedTweets.csv', 'r', newline='', encoding="utf8") as csvfile: # open training data
        b = 0 # keeps track of how many tweets we have trained on so far
        reader = csv.reader(csvfile)
        dem_tweets = ["Trump Sucks"] # need to put at least on tweet in to get into the while loop
        rep_tweets = ["Biden Sucks"]
        while dem_tweets != [] or rep_tweets != []: # if we have no tweets left to train on then stop training
            print("Training pass starting, b: " + str(b))
            dem_tweets, rep_tweets, reader, key = pullSomeTestData(3000, reader) # pull dem, and rep tweets, a key for the tweets, and the reader to pass back
            if dem_tweets == [] and rep_tweets == []: # if it gave us back no tweets then we are done training
                break
            b += 3000 # increment b
            tweets = vectorizer.transform(dem_tweets+rep_tweets) # vectorize and combine the rep and dem tweets
            clf.partial_fit(tweets, key, classes=["Democrat","Republican"], sample_weight=1) # partial fit to the new tweets
        return clf # return the classifier when the while loop ends

# for use inside of the big_training() function
# pulls n lines from reader, and finds republican, democrat tweets and creates a key for the tweets
# it returns all of those things plus the reader
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

# creates the classifier and vectorizer and returns them
def create_classifier():
    vectorizer = HashingVectorizer(stop_words='english', alternate_sign=False)
    classifier = big_training()
    return classifier, vectorizer

# classifies a list of tweets and returns it
def classify_tweet(cs, vect, tweets):
    return cs.predict(vect.transform(tweets))

#classifier a list of tweets, counts the number of reps and dems and returns those numbers
def classify_tweets_count(cs, vect, tweets):
    ef = cs.predict(vect.transform(tweets))
    dem = 0
    rep = 0
    for g in ef:
        print(g)
        if g == "Democrat":
            dem += 1
        else:
            rep += 1
    return dem, rep

if __name__ == "__main__":
    tqr = [""]
    tqd = [""]
    ans = pullTestData(tqr, tqd)
    classifier, vectorizer = create_classifier()
    #test_tweet_questions = vectorizer.transform(tqr + tqd)
    test_tweet_questions = tqr + tqd
    ef = classify_tweet(classifier, vectorizer, test_tweet_questions)
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