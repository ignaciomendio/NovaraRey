from django.urls import path
from StaffApp.views import *


urlpatterns = [
    path('dashboard/', vista_dashboard, name='dashboard'),
    path('', vista_enter, name='enter'),
    path('tareas/', vista_tareas_main, name='tareas_main'),
    path('tareas/edit/<int:id>/', vista_tareas_edit, name='tareas_edit'),
    path('tareas/create/', vista_tareas_create, name='tareas_create'),
    path('tareas/export/', vista_tareas_export, name='tareas_export_excel'),
    path('prestadores/', vista_prestadores_main, name='prestadores_main'),
    path('prestadores/create/', vista_prestadores_create, name='prestadores_create'),
    path('prestadores/edit/<int:id>/', vista_prestadores_edit, name='prestadores_edit'),
    path('prestadores/doc/', vista_prestadores_doc, name='prestadores_doc'),
    path('aseguradoras/', vista_aseguradoras_main, name='aseguradoras_main'),
    path('aseguradoras/create/', vista_aseguradoras_create, name='aseguradoras_create'),
    path('aseguradoras/edit/<int:id>/', vista_aseguradoras_edit, name='aseguradoras_edit'),
    path('aseguradoras/edit/telAdd/<int:id>/', vista_aseguradoras_edit_telAdd, name='telefono_add'),
    path('aseguradoras/edit/mailAdd/<int:id>/', vista_aseguradoras_edit_mailAdd, name='mail_add'),
    path('aseguradoras/edit/telEdit/<int:id>/', vista_aseguradoras_edit_telEdit, name='tel_edit'),
    path('aseguradoras/edit/mailEdit/<int:id>/', vista_aseguradoras_edit_mailEdit, name='mail_edit'),
    path('aseguradoras/edit/telDelete/<int:id>/', vista_aseguradoras_edit_telDelete, name='tel_delete'),
    path('aseguradoras/edit/mailDelete/<int:id>/', vista_aseguradoras_edit_mailDelete, name='mail_delete'),
]

