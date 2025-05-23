from django.db import models


# Create your models here.

class RubroCat(models.Model):
    created = models.DateField(verbose_name="Fecha de pedido", auto_now_add=True)
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    
    class Meta:
        verbose_name="Categoría"
        verbose_name_plural="Categorías"

    def __str__(self):
        return self.nombre
    

class Categoria(models.Model):
    created = models.DateField(verbose_name="Fecha de pedido", auto_now_add=True)
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    imagen = models.ImageField(upload_to="RubrosMedia", verbose_name="Imagen")
    rubro = models.ForeignKey(RubroCat, on_delete=models.CASCADE, verbose_name="Rubro", related_name="categorias")
    
    class Meta:
        verbose_name="Tipo de seguro"
        verbose_name_plural="Tipos de seguro"

    def __str__(self):
        return self.nombre
