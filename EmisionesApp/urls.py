from django.urls import path
from .views import *


urlpatterns = [
    path('add/<int:id>', vista_new_emision, name='new_emision'),
    path('list', vista_ver_emisiones, name='ver_emisiones'),
    path('edit/<int:id>',vista_editar_emision, name='edita_emision'),
    path('edit/addfile/<int:id>', vista_add_file_emision, name="add_file_emision"),
    path('edit/delfile/<int:emision_id>/<int:file_id>/', vista_del_file_emision, name="del_file_emision"),

]

