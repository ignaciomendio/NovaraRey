from django.contrib import admin

from django.contrib import admin
from .models import RubroPrestador, Prestador

class RubroPrestadorAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)
    ordering = ("nombre",)

class PrestadorAdmin(admin.ModelAdmin):
    list_display = ("rubro", "nombre", )
    search_fields = ("nombre", "contacto", "rubro")
    list_filter = ("rubro", "activo")
    ordering = ("rubro__nombre", "nombre")
    readonly_fields = ("fecha_creacion",)

admin.site.register(RubroPrestador, RubroPrestadorAdmin)
admin.site.register(Prestador,PrestadorAdmin)


