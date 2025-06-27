from django.urls import path
from .views import *


urlpatterns = [
    path('add/<int:id>', vista_new_emision, name='new_emision'),
    path('addPoliza/<int:id>/', vista_add_poliza, name='add_poliza'),
    path('verPoliza/<int:id>/', vista_ver_poliza, name='ver_poliza'),
    path('dowloadFile/<int:id>/', descargar_archivo, name='download_file_emision'),
    path('listpolizas', vista_list_polizas, name='list_polizas'),
    path('list', vista_ver_emisiones, name='ver_emisiones'),
    path('edit/addfile/<int:id>', vista_add_file_emision, name="add_file_emision"),
    path('edit/delfile/<int:emision_id>/<int:file_id>/', vista_del_file_emision, name="del_file_emision"),
    path('editemision/<int:id>/',vista_editar_emision_completa, name='editar_emision_completa'),
    path('cancelemision/<int:id>/',vista_cancelar_emision, name='cancelar_emision'),
    path('editEndoso/<int:id>/', vista_editar_endoso, name='edit_endoso'),
    path('endoso/modificación/<int:id>/', vista_endoso_modificacion, name='endoso_modificacion'),
    path('addobservacion/<int:id>/', vista_add_observacion_emision, name='add_observacion'),
    path('poliza/no_renovar/<int:id>/', vista_no_renovar_poliza, name='no_renovar_poliza'),
    path('poliza/anular/<int:id>/', vista_anular_poliza, name='anular_poliza'),
    path('poliza/reactivar/<int:id>/', vista_reactivar_poliza, name='reactivar_poliza'),
    path('poliza/modificar/<int:id>/', vista_modificar_poliza, name='modificar_poliza'),
    path('poliza/modificar_conducto/<int:id>/', vista_modificar_conducto, name='modificar_conducto'),

]

