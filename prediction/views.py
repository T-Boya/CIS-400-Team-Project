from django.shortcuts import render, redirect
from django.http import HttpResponse
import asyncio, requests, httpx, time
from asgiref.sync import sync_to_async
from django.contrib.staticfiles.finders import find
import csv
from .live_data_analyzer import Current_Tweets_Sentiment, oauth_login
# Vars for Archived Data

# new architecture: home page does not redirect on data collection but alerts user. data collection page has a 'recollect' option
# instead of a 'clear data' option

def within_date_range(start_date, end_date, archive_date):
    start_date = [int(start_date[:-4]), int(start_date[-4:-2]), int(start_date[-2:])]
    end_date = [int(end_date[:-4]), int(end_date[-4:-2]), int(end_date[-2:])]
    archive_date = [int(archive_date[:-4]), int(archive_date[-4:-2]), int(archive_date[-2:])]
    if archive_date[2] >= start_date[2] and archive_date[2] <= end_date[2]:
        if archive_date[2] == start_date[2] and archive_date[2] != end_date[2]:
            if archive_date[0] > start_date[0]:
                return True
            elif archive_date[0] == start_date[0]:
                if archive_date[1] >= start_date[1]:
                    return True
        elif archive_date[2] == end_date[2] and archive_date[2] != start_date[2]:
            if archive_date[0] < end_date[0]:
                return True
            elif archive_date[0] == end_date[0]:
                if archive_date[1] <= end_date[1]:
                    return True
        elif archive_date[2] == start_date[2] == end_date[2]:
            if archive_date[0] >= start_date[0] and archive_date[0] <= end_date[0]:
                if archive_date[0] > start_date[0] and archive_date[0] < end_date[0]:
                    return True
                else:
                    if archive_date[0] == start_date[0] and start_date[0] != end_date[0]:
                        if archive_date[1] >= start_date[1]:
                            return True
                    elif archive_date[0] == end_date[0] and start_date[0] != end_date[0]:
                        if archive_date[1] <= end_date[1]:
                            return True
                    elif archive_date[1] >= start_date[1] and archive_date[1] <= end_date[1]:
                        return True
        else:
            return True
    return False

# Create your views here.
def index(request):
    # if request.session['data_loaded']:
    #     return redirect(view_live)
    context = {}
    return render(request, 'index.html', context)

# load live twitter data
def load_live(request):
    democrat_kwarg_list = 'biden, democratic, democrat' # API is case insensitive
    republican_kwarg_list = 'trump, republican, gop'
    # bipartisan_kwarg_list = democrat_kwarg_list + ', ' + republican_kwarg_list
    democrats, dem_tweets, republicans, rep_tweets = Current_Tweets_Sentiment(bipartisan_kwarg_list, 100)
    # democrats = 150
    # dem_tweets = []
    # republicans = 50
    # rep_tweets = []
    print('in the view now')
    print("Democratic: ", democrats, " Republican: ", republicans)
    winner = "DEMOCRATS" if democrats > republicans else "REPUBLICANS"
    vote_share = democrats * 100 / (democrats + republicans)
    winner_vote_share= (democrats * 100 / (democrats + republicans)) if democrats > republicans else (republicans * 100 / (democrats + republicans))
    pie_chart = "radial-gradient( circle closest-side, transparent 66%, white 0), conic-gradient(#4e79a7 0, #4e79a7 {}%, #edc949 0, #edc949 100%);".format(vote_share)
    context  = {"winner" : winner,
                "democrats" : democrats,
                "republicans" : republicans,
                "total" : (democrats + republicans),
                "vote_share" : vote_share,
                "pie_chart" : pie_chart,
                "winner_vote_share" : winner_vote_share,
                "dem_tweets" : dem_tweets[:10],
                "rep_tweets": rep_tweets[:10],}
    return render(request, 'live_results.html', context)

def load_archive(request, start_date, end_date):
    dem_votes_lst = []
    rep_votes_lst = []
    with open(find('TXT/past_tweet_analysis.txt'), 'r') as archive_data:
        found_matches = False
        for line in archive_data:
            contents = line.split()
            archive_date_raw = contents[0].split('/')
            archive_date = ''.join(archive_date_raw)
            if within_date_range(start_date, end_date, archive_date):
                found_matches = True
                rep_votes_lst.append(int(contents[1])) # ask daniel if this is rep or dem column
                dem_votes_lst.append(int(contents[2]))
            else:
                if found_matches:
                    break
    if len(rep_votes_lst) == 0:
        return HttpResponse('Invalid Date Range')
    dem_votes = sum(dem_votes_lst)
    rep_votes = sum(rep_votes_lst)
    winner = "DEMOCRATS" if dem_votes > rep_votes else "REPUBLICANS"
    ratio_lst = []
    for i in range(len(dem_votes_lst)):
        if winner == "DEMOCRATS": ratio_lst.append((100 * dem_votes_lst[i])/(rep_votes_lst[i] + dem_votes_lst[i]))
        else: ratio_lst.append((100 * rep_votes_lst[i])/(dem_votes_lst[i] + rep_votes_lst[i]))
    chart_data = '['
    x_vals = '['
    for i in range(len(ratio_lst)):
        # chart_data += '{x:' + str(i) + ", y:" + str(ratio_lst[i]) + "},"
        chart_data += str(ratio_lst[i]) + ","
        x_vals += str(i) + ","
    chart_data = chart_data[:-1] + "]"
    x_vals = x_vals[:-1] + "]"
    winner_vote_share = int((dem_votes * 100 / (dem_votes + rep_votes)) if dem_votes > rep_votes else (rep_votes * 100 / (dem_votes + rep_votes)))
    context  = {
        "winner" : winner,
        "winner_vote_share" : winner_vote_share,
        "total" : (dem_votes + rep_votes),
        "ratio_lst" : ratio_lst,
        "dem_votes_list" : dem_votes_lst,
        "rep_votes_list" : rep_votes_lst,
        "chart_data" : chart_data,
        "x_vals" : x_vals,
    }
    return render(request, 'archive_results.html', context)

# load view controller: will take user to appropriate page when live data loading is requested
def loading_live(request):
    context = {}
    if request.session['data_loaded']:
        return redirect(live_results)
    elif request.session['loading_live']:
        return render(request, 'loading_live.html', context)
    else:
        return redirect(load_live)

def live_results(request):
    time.sleep(10)
    if not request.session['data_loaded']:
        return redirect(index)
    context = {
        'ip' : request.session['ip'],
        'country' : request.session['country'],
    }
    return render(request, 'results.html', context)


# async def gather_data(request):