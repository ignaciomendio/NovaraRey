from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from datetime import datetime

def vista_home(req:HttpRequest)->HttpResponse:
    return render(req, "MainApp/home.html", {"year": datetime.now().year})

def vista_sobre_nosotros(req:HttpRequest)->HttpResponse:
    pass

def vista_servicios(req:HttpRequest)->HttpResponse:
    pass

def vista_contacto(req:HttpRequest)->HttpResponse:
    pass
