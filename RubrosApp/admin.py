from django.contrib import admin
from .models import RubroCat, Categoria

# Register your models here.

class RubroCatAdmin(admin.ModelAdmin):
    readonly_fields=("created",)
    list_display = ("nombre",)
    search_fields = ("nombre",)

class CategoriaAdmin(admin.ModelAdmin):
    readonly_fields=("created",)
    list_display = ("nombre",)
    search_fields = ("nombre",)

admin.site.register(RubroCat, RubroCatAdmin)
admin.site.register(Categoria, CategoriaAdmin)