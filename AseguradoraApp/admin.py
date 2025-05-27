from django.contrib import admin
from .models import Cia, CiaTelContact, CiaMailContact

class CiaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cuit", "direccion")
    search_fields = ("nombre", "cuit")
    ordering = ("nombre",)

class CiaTelContactAdmin(admin.ModelAdmin):
    list_display = ("telefono", "contacto", "cia")
    search_fields = ("telefono", "contacto", "cia__nombre")
    ordering = ("telefono",)

class CiaMailContactAdmin(admin.ModelAdmin):
    list_display = ("mail", "contacto", "cia")
    search_fields = ("mail", "contacto","cia__nombre")
    ordering = ("mail",)

admin.site.register(Cia, CiaAdmin)
admin.site.register(CiaTelContact,CiaTelContactAdmin)
admin.site.register(CiaMailContact,CiaMailContactAdmin)


# Register your models here.
