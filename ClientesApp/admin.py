from django.contrib import admin

from .models import (
    TelefonoCte, EmailCte,
    ClientePersonaFisica, ClientePersonaJuridica
)

admin.site.register(TelefonoCte)
admin.site.register(EmailCte)

@admin.register(ClientePersonaFisica)
class ClientePersonaFisicaAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'dni', 'condicion_iva')
    search_fields = ('apellido', 'nombre', 'dni')
    list_filter = ('condicion_iva',)
    filter_horizontal = ('telefonos', 'emails')

@admin.register(ClientePersonaJuridica)
class ClientePersonaJuridicaAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'cuit', 'condicion_iva')
    search_fields = ('razon_social', 'cuit')
    list_filter = ('condicion_iva',)
    filter_horizontal = ('telefonos', 'emails')

