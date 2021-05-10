import time
import sentiment_analysis
import twitter
import requests
from requests_oauthlib import OAuth1


def analyize_tweets(month, day, year, au, classifier, wf, wfile):
    if month < 10:
        smonth = "0" + str(month)
    else:
        smonth = str(month)
    if day < 10:
        sday = "0" + str(day)
    else:
        sday = str(day)
    with open("us-pres-elections-2020/20" + str(year) + "-" + smonth + "/us-presidential-tweet-id-20"
         + str(year) + "-" + smonth + "-" + sday + "-00.txt", "r", newline='') as twFile:
        num_ids = 0
        calls_for_this_file = 0
        ids = ""
        rep = 0
        dem = 0
        for id in twFile:
            if num_ids < 99:
                ids = ids + id.strip() + ","
                num_ids += 1
            else:
                if num_ids < 100:
                    ids = ids + id.strip()
                    num_ids += 1
                try:
                    s = requests.get("https://api.twitter.com/1.1/statuses/lookup.json?", params={'id': ids}, auth=au)
                    if s.status_code != 200:
                        if s.json()["errors"][0]["code"] == "88":
                            raise RuntimeError("Hit Rate Limit")
                        else:
                            print("Bad Response from twitter. Exiting program")
                            twFile.close()
                            return 0
                    for t in s.json():
                        guess = sentiment_analysis.classify_tweet(classifier, wf, t["text"])
                        if guess == "Democrat":
                            dem += 1
                        else:
                            rep += 1
                    print("Dem: " + str(dem) + ", Rep: " + str(rep))
                    ids = ""
                    num_ids = 0
                    if calls_for_this_file < 20 and dem + rep <= 1000:
                        calls_for_this_file += 1
                    else:
                        wfile.write(str(month) + "/" + str(day) + "/" + str(year) + " " + str(rep) + " " + str(dem) + "\n")
                        twFile.close()
                        return 1
                except RuntimeError as e:
                    print('Encountered 429 Error (Rate Limit Exceeded)')  # I took this code from the cookbook
                    print("Retrying in 15 minutes...ZzZ...")  # nice print statements I like them
                    time.sleep(60 * 15 + 5)
                    print('...ZzZ...Awake now and trying again.')


if __name__ == "__main__":
    """
    myAuth = twitter.oauth.OAuth(consumer_key='cvUnT3e5uMm7URiYZscsED8DF',  # just auth stuff
                                 consumer_secret='IfFSYmujlz2F3HlKQk8mZ6sgZc10646pniF2Utvd8lEx4l1Ckg',
                                 token='980873561886937088-jgzxBfvmibqClm8twVLzqFiUBHvK4ua',
                                 token_secret='QNTPfO6UKO92t6ECZb2o8L9Dig2uYtSn2OSi5ApOuqQSC')
    tw = twitter.Twitter(auth=myAuth)
    """
    au = OAuth1('cvUnT3e5uMm7URiYZscsED8DF', 'IfFSYmujlz2F3HlKQk8mZ6sgZc10646pniF2Utvd8lEx4l1Ckg', "980873561886937088-jgzxBfvmibqClm8twVLzqFiUBHvK4ua", 'QNTPfO6UKO92t6ECZb2o8L9Dig2uYtSn2OSi5ApOuqQSC')
    classifier, wf = sentiment_analysis.create_classifier()
    print("Classifier created")
    with open("past_tweet_analysis.txt", "a") as output:
        year = 21
        day = 1
        month = 3
        while year != 21 or month != 5:
            worked = analyize_tweets(month, day, year, au, classifier, wf, output)
            if worked != 0:
                print("Analyized " + str(month) + "/" + str(day) + "/" + str(year))
                if day == 31 or (day == 30 and (month == 4 or month == 6 or month == 9 or month == 11)) or (month == 2 and day == 29 and (year%4 != 0)) or (month == 2 and day == 28 and (year%4 != 0)):
                    if month == 12:
                        year += 1
                        month = 1
                        day = 1
                    else:
                        day = 1
                        month += 1
                else:
                    day += 1
            else:
                break
        output.close()


