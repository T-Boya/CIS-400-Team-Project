import time
import sentiment_analysis
import requests
from requests_oauthlib import OAuth1

# given a starting month, day, year, classifier, and a file to look through
# pull out tweet ids, classifiy about 1000 tweets for that day, write the number of rep and dem tweets to a file
# then move on to the next day and continue until we run out of data to look thorugh
def analyize_tweets(month, day, year, au, classifier, wf, wfile):
    if month < 10: # this stuff just normalizes the month and day strings so we can use them to find a file in the directory
        smonth = "0" + str(month)
    else:
        smonth = str(month)
    if day < 10:
        sday = "0" + str(day)
    else:
        sday = str(day)
    with open("us-pres-elections-2020/20" + str(year) + "-" + smonth + "/us-presidential-tweet-id-20"
         + str(year) + "-" + smonth + "-" + sday + "-00.txt", "r", newline='') as twFile: # put the data together and use it to find the file we are looking for
        num_ids = 0
        calls_for_this_file = 0 # if we make more than 20 api calls for one day we just move on for rate limiting reasons
        ids = "" # we have to send the ids in strings so we start that here
        rep = 0 # how many reps and dems we have found so far
        dem = 0
        for id in twFile: # for each id in the file
            if num_ids < 99: # if we have less than 99 ids then just keep looking for ids
                ids = ids + id.strip() + ","
                num_ids += 1
            else:
                if num_ids < 100: # after 99 ids add the last one
                    ids = ids + id.strip()
                    num_ids += 1
                try: # then send the 100 ids to twitter to get back the full text
                    s = requests.get("https://api.twitter.com/1.1/statuses/lookup.json?", params={'id': ids}, auth=au)
                    if s.status_code != 200:
                        if s.json()["errors"][0]["code"] == 88: # rate limit catching
                            raise RuntimeError("Hit Rate Limit")
                        else:
                            print("Bad Response from twitter. Exiting program")
                            print(s.json())
                            twFile.close()
                            return 0
                    tweets = []
                    for t in s.json(): # put all the tweets into one list so we can classify them
                        tweets.append(t["text"])
                    dem_t, rep_t = sentiment_analysis.classify_tweets_count(classifier, wf, tweets) # classify them
                    dem += dem_t # add the number of dems and reps to the totals for the day
                    rep += rep_t
                    print("Dem: " + str(dem) + ", Rep: " + str(rep))
                    ids = "" # reset the id string and number of id var
                    num_ids = 0
                    if calls_for_this_file < 20 and dem + rep <= 1000: # if we have found at least 1000 total tweets or we have made 20 api calls then we write this day to our output file and move on
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
    au = OAuth1('cvUnT3e5uMm7URiYZscsED8DF', 'IfFSYmujlz2F3HlKQk8mZ6sgZc10646pniF2Utvd8lEx4l1Ckg', "980873561886937088-jgzxBfvmibqClm8twVLzqFiUBHvK4ua", 'QNTPfO6UKO92t6ECZb2o8L9Dig2uYtSn2OSi5ApOuqQSC')
    classifier, wf = sentiment_analysis.create_classifier()
    print("Classifier created")
    with open("past_tweet_analysis.txt", "a") as output:
        year = 20
        day = 1
        month = 3
        while year != 21 or month != 5:
            worked = analyize_tweets(month, day, year, au, classifier, wf, output)
            if worked != 0:
                print("Analyized " + str(month) + "/" + str(day) + "/" + str(year))
                if day == 31 or (day == 30 and (month == 4 or month == 6 or month == 9 or month == 11)) or (month == 2 and day == 29 and (year%4 == 0)) or (month == 2 and day == 28 and (year%4 != 0)):
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


