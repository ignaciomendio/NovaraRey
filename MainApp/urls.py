from django.urls import path
from MainApp.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', vista_home, name='home'),

]

urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)