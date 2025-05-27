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
    path('prestadores/sendmail', vista_prestadores_sendmail, name='prestadores_enviar_mail'),
    path('prestadores/create/', vista_prestadores_create, name='prestadores_create'),
    path('prestadores/edit/<int:id>/', vista_prestadores_edit, name='prestadores_edit'),
]

