from django.urls import path
from .views import *


urlpatterns = [
    path('', vista_productores, name='productores'),
    path('add/', vista_add_productor, name='add_productor'),
    path('edit/<int:id>/', vista_edit_productor, name='edit_productor'),
    path('delete/<int:id>/', vista_delete_productor, name='delete_productor'),
    path('addcodigo/', vista_add_codigo, name='add_codigo'),
    path('codigo/edit/<int:id>/', vista_edit_codigo, name='edit_codigo'),
    path('codigo/toggle/<int:id>/', vista_toggle_codigo, name='toggle_codigo'),

]

