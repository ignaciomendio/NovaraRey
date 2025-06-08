from django.urls import path
from RubrosApp.views import *


urlpatterns = [
    path('', vista_rubros, name='rubros'),
    path('more_info', more_info, name='more_info'),
    

]

