from django.contrib import admin
from .models import Address, AdressType

class AddressAdmin(admin.ModelAdmin):
    list_display = ("calle", "numero", "localidad", "provincia")
    search_fields = ("calle", "localidad", "provincia")

class AdressTypeAdmin(admin.ModelAdmin):
    list_display = ("tipo",)
    search_fields = ("tipo",)


admin.site.register(Address)
admin.site.register(AdressType) 

# Register your models here.
