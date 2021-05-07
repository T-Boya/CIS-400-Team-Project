from django.shortcuts import render, redirect
from django.http import HttpResponse
import asyncio, requests, httpx, time
from asgiref.sync import sync_to_async
# Vars for Archived Data


# Testing API
print('getting response')
response = requests.get('https://jsonplaceholder.typicode.com/todos/1')
print('this is the response:')
print(response)

async def test_func():
    await time.sleep(10)
    print('done')


# Create your views here.
def index(request):
    if request.session['data_loaded']:
        return redirect(view_live)
    context = {}
    return render(request, 'index.html', context)

@sync_to_async
def load_live(request):
    request.session['loading_live'] = True # check this var to prevent ultiple instances of async func running
    time.sleep(10)
    request.session['ip'] = 7
    request.session['country'] = 'Kenya'
    request.session['data_loaded'] = True
    request.session['loading_live'] = False
    return redirect(view_live)

def clear_live(request):
    request.session['data_loaded'] = False
    return redirect(index)

def view_live(request):
    if not request.session['data_loaded']:
        return redirect(index)
    context = {
        'ip' : request.session['ip'],
        'country' : request.session['country'],
    }
    return render(request, 'live_loaded.html', context)


# async def gather_data(request):