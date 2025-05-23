from django.shortcuts import render
from django.http import HttpResponse, HttpRequest

def vista_home(req:HttpRequest)->HttpResponse:
    return render(req, "MainApp/home.html", {"year": 2023})

