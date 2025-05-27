from django.urls import path
from AseguradoraApp.views import *


urlpatterns = [
    path('', vista_aseguradora, name='aseguradoras'),
    

]

