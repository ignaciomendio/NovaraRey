from django.urls import path
from ClientesApp.views import *


urlpatterns = [
    path('', vista_clientes, name='clientes_main'),
    path('edit/<int:id>/', cliente_edit, name='cliente_edit'),
    path('nuevo/<str:typ>', cliente_create, name='cliente_create'),
    path('borrar/<int:id>/', cliente_delete, name='cliente_delete'),
    path('edit/telAdd/<int:id>/', cliente_edit_teladd, name='telefono_add_cte'),
    path('edit/mailAdd/<int:id>/', cliente_edit_mailadd, name='mail_add_cte'),
    path('edit/telEdit/<int:id>/', cliente_edit_teledit, name='tel_edit_cte'),
    path('edit/mailEdit/<int:id>/', cliente_edit_mailedit, name='mail_edit_cte'),
    path('edit/telDelete/<int:id>/', cliente_edit_teldel, name='tel_delete_cte'),
    path('edit/mailDelete/<int:id>/', cliente_edit_maildel, name='mail_delete_cte'),
    path('edit/tarjetaAdd/<int:id>/', cliente_edit_tarjetaadd, name='tarjeta_add_cte'),
    path('edit/transferenciaAdd/<int:id>/', cliente_edit_transferenciaadd, name='transferencia_add_cte'),
    path('edit/tarjetaDelete/<int:id>/', cliente_edit_tarjetadel, name='tarjeta_delete_cte'),
    path('edit/transferenciaDelete/<int:id>/', cliente_edit_transferenciadel, name='transferencia_delete_cte'),
    path('edit/tarjetaEdit/<int:id>/', cliente_edit_tarjetaedit, name='tarjeta_edit_cte'),
    path('edit/transferenciaEdit/<int:id>/', cliente_edit_transferenciaedit, name='transferencia_edit_cte'),
    path('edit/medioDelete/<int:id>/', cliente_edit_mediodel, name='medio_delete_cte'),
]


