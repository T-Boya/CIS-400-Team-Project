from django.shortcuts import render, redirect
from django.http import HttpResponse
import asyncio, requests, httpx, time
from asgiref.sync import sync_to_async
from .live_data_analyzer import Current_Tweets_Sentiment, oauth_login
# Vars for Archived Data

# new architecture: home page does not redirect on data collection but alerts user. data collection page has a 'recollect' option
# instead of a 'clear data' option

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
    bipartisan_kwarg_list = democrat_kwarg_list + ', ' + republican_kwarg_list
    democrats, republicans = Current_Tweets_Sentiment(bipartisan_kwarg_list, 200)
    # democrats = 150
    # republicans = 50
    print('in the view now')
    print("Democratic: ", democrats, " Republican: ", republicans)
    winner = "DEMOCRATS" if democrats > republicans else "REPUBLICANS"
    vote_share = democrats * 100 / (democrats + republicans)
    pie_chart = "radial-gradient( circle closest-side, transparent 66%, white 0), conic-gradient(#4e79a7 0, #4e79a7 {}%, #edc949 0, #edc949 100%);".format(vote_share)
    context  = {"winner" : winner,
                "democrats" : democrats,
                "republicans" : republicans,
                "total" : (democrats + republicans),
                "vote_share" : vote_share,
                "pie_chart" : pie_chart}
    return render(request, 'results.html', context)

def load_archive(request):
    time.sleep(5)
    context  = {}
    return render(request, 'results.html', context)

# load view controller: will take user to appropriate page when live data loading is requested
def loading_live(request):
    context = {}
    if request.session['data_loaded']:
        return redirect(results)
    elif request.session['loading_live']:
        return render(request, 'loading_live.html', context)
    else:
        return redirect(load_live)

def results(request):
    time.sleep(10)
    if not request.session['data_loaded']:
        return redirect(index)
    context = {
        'ip' : request.session['ip'],
        'country' : request.session['country'],
    }
    return render(request, 'results.html', context)


# async def gather_data(request):