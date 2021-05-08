from django.shortcuts import render, redirect
from django.http import HttpResponse
import asyncio, requests, httpx, time
from asgiref.sync import sync_to_async

# Vars for Archived Data


# # Testing API
# print('getting response')
# response = requests.get('https://jsonplaceholder.typicode.com/todos/1')
# print('this is the response:')
# print(response)

async def test_func():
    await time.sleep(10)
    print('done')


# new architecture: home page does not redirect on data collection but alerts user. data collection page has a 'recollect' option
# instead of a 'clear data' option

# Create your views here.
def index(request):
    # if request.session['data_loaded']:
    #     return redirect(view_live)
    context = {}
    return render(request, 'index.html', context)

# load live twitter data
# @shared_task(bind=True)
def load_live(request):
    # progress_recorder.set_progress(i + 1, seconds, description=nasa_image_result)
    request.session['loading_live'] = True # check this var to prevent ultiple instances of async func running
    time.sleep(1)
    request.session['ip'] = 7
    request.session['country'] = 'Kenya'
    request.session['data_loaded'] = True
    request.session['loading_live'] = False
    return redirect(view_live)

# load view controller: will take user to appropriate page when live data loading is requested
def loading_live(request):
    context = {}
    if request.session['data_loaded']:
        return redirect(results)
    elif request.session['loading_live']:
        return render(request, 'loading_live.html', context)
    else:
        return redirect(load_live)

def clear_live(request):
    request.session['data_loaded'] = False
    return redirect(index)

def results(request):
    time.sleep(10)
    if not request.session['data_loaded']:
        return redirect(index)
    context = {
        'ip' : request.session['ip'],
        'country' : request.session['country'],
    }
    return render(request, 'results.html', context)

def load_archive(request):
    context  = {}
    return render(request, 'load_archive.html', context)


# async def gather_data(request):