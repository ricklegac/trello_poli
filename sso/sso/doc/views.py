from http.client import HTTPResponse
from django.shortcuts import render, HttpResponse

# Create your views here.
def home(request):
    return HttpResponse("<h1>Proyecto IS2</h1><h2>Vista</h2>") 