from django.urls import path
from .views import vista_add_comment, vista_ver_pagos, vista_pagar_cuota


urlpatterns = [
    path('listpagos', vista_ver_pagos, name='ver_pagos'),
    path('addComment/<int:pk>', vista_add_comment, name='editar_observaciones_cuota'),
    path('pagar/<int:pk>', vista_pagar_cuota, name='pagar_cuota'),

]

