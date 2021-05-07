"""president_predictor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('view_live/', views.view_live, name='view_live'),
    path('load_live/', views.load_live, name='load_live'),
    path('clear_live/', views.clear_live, name='clear_live'),
    # path('loading_live/', view.loading_live, name='loading_live')
    # path('/gather_data', views.gather_data, name='gather_data')
]
