from django.shortcuts import render
from RubrosApp.models import Categoria
from django.http import HttpResponse, HttpRequest    

# Create your views here.
def vista_rubros(request:HttpRequest)->HttpResponse:
    rubros = Categoria.objects.all()
    return render(request, 'RubrosApp/rubros.html',{"rubros": rubros})