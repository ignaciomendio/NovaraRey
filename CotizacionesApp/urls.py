from django.urls import path
from .views import *


urlpatterns = [
    path('nuevasolicitud/', vista_crear_solicitud, name='crear_solicitud_cotizacion'),
    path('solicitudes/', vista_ver_solicitudes, name='ver_solicitudes_cotizacion'),
    path('listado/', vista_ver_cotizaciones, name='ver_cotizaciones'),
    path('solicita/', vista_solicitar, name='solicita_cot'),
    path('solicitudes/edit/<int:id>', vista_edit_solicitud, name='edit_solicitud'),
    path('solicitudes/cancel/<int:id>', vista_cancel_solicitud, name='cancel_solicitud'),
    path('cancel/<int:id>', vista_cancel_cotizacion, name='cancel_cotizacion'),
    path('solicitudes/cotizar/<int:id>', vista_cotizar_solicitud, name='cotizar_solicitud'),
    path('cot_cias/edit/<int:id>/', vista_edit_cot_cia, name='edit_cot_cia'),
    path('cot_cias/delete/<int:idcot>/<int:idcot_cia>/', vista_del_cot_cia, name='del_cot_cia'),
    path('cot_cias/add/', vista_add_cot_cia, name='add_cotizacion_cia'),
    path('edit/<int:id>', vista_editar_cotizacion, name='editar_cotizacion'),
    path('send/<int:id>', vista_send_cotizacion, name='send_cotizacion'),
]

