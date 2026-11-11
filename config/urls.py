from django.contrib import admin
from django.urls import path
from market import views
from market.mobile import mobile_api

urlpatterns = [path('', views.index), path('admin/', admin.site.urls), path('api/<str:action>/', views.api), path('mobile-api/<str:action>/', mobile_api)]
