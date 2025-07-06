from django.urls import path
from .views import *


urlpatterns = [
    path('add/<int:id>', vista_nuevo_siniestro, name='nuevo_siniestro'),
    path('edit/<int:id>', vista_edit_siniestro, name='editar_siniestro'),
    path('list', vista_list_siniestros, name="list_siniestros"),
    path('add_note/<int:id>', vista_add_note, name='add_note'),
    path('add_tercero/<int:id>', vista_add_tercero, name='add_tercero'),
    path('edit_tercero/<int:id>', vista_edit_tercero, name='edit_tercero'),
    path('del_tercero/<int:sinid>/<int:terid>', vista_del_tercero, name='del_tercero'),
    path('add_file/<int:id>', vista_add_file_siniestro, name='add_file_siniestro'),
    path('add_voucher/<int:id>', vista_add_voucher, name='add_voucher'),
    path('del_archivo/<int:sinid>/<int:fileid>', vista_del_archivo, name='del_archivo'),
    path('informar_sin/<int:id>', vista_informar_sin, name='informar_sin'),
    path('resolver_sin/<int:id>', vista_resolver_sin, name='resolver_siniestro'),
    path('rechazar_sin/<int:id>', vista_rechazar_sin, name='rechazar_siniestro'),
]


