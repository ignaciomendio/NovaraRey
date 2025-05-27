from django.shortcuts import render
from .models import Cia

def vista_aseguradora(request):
    aseguradoras = Cia.objects.all()
    return render(request, 'AseguradoraApp/aseguradoras.html', {'aseguradoras': aseguradoras})


