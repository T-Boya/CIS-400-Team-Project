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
    democrat_kwarg_list = 'Biden, biden, Democratic, democratic, Democrat, democrat'
    republican_kwarg_list = 'Trump, trump, Republican, republican, GOP, gop'
    bipartisan_kwarg_list = democrat_kwarg_list + ', ' + republican_kwarg_list
    dem, rep = Current_Tweets_Sentiment(bipartisan_kwarg_list, 200)
    print("Democratic: ", dem, " Republican: ", rep)
    context  = {}
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