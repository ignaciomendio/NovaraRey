from django.contrib import admin
from .models import DataCotizacion, QuotRequest, Cotizacion, DataEmision

class DataCotizacionAdmin(admin.ModelAdmin):
    list_display = ('rubro', 'nombre_dato', 'tipo_dato')
    search_fields = ('rubro',)
    list_filter = ('rubro',)

class DataEmisionAdmin(admin.ModelAdmin):
    list_display = ('rubro', 'data', 'requerido')
    list_filter = ('rubro',)

admin.site.register(DataCotizacion, DataCotizacionAdmin)
admin.site.register(QuotRequest)
admin.site.register(Cotizacion)
admin.site.register(DataEmision, DataEmisionAdmin)

