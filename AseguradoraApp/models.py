from django.db import models
from MainApp.models import Address

class CiaTelContact(models.Model):
    telefono = models.CharField(max_length=50, verbose_name="Teléfono")
    contacto = models.CharField(max_length=50, verbose_name="Contacto")
    desc = models.CharField(max_length=100, verbose_name="Descripción del contacto", null=True, blank=True)
    cia=models.ForeignKey("Cia", on_delete=models.CASCADE, verbose_name="Compañía")
    
    class Meta:
        verbose_name="teléfono de Contacto"
        verbose_name_plural="Teléfonos de contacto"

    def __str__(self):
        return self.telefono + " - " + self.contacto + " - " + self.desc
    

class CiaMailContact(models.Model):
    mail = models.EmailField(max_length=50, verbose_name="Mail")
    contacto = models.CharField(max_length=50, verbose_name="Contacto")
    desc = models.CharField(max_length=100, verbose_name="Descripción del contacto", null=True, blank=True)
    cia=models.ForeignKey("Cia", on_delete=models.CASCADE, verbose_name="Compañía")
    
    class Meta:
        verbose_name="mail de Contacto"
        verbose_name_plural="Mails de contacto"

    def __str__(self):
        return self.mail + " - " + self.contacto + " - " + self.desc
    
class Cia(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre de la compañía")
    cuit = models.CharField(max_length=15, verbose_name="CUIT de la compañía")
    activa = models.BooleanField(default=True, verbose_name="Compañía activa")
    logoUrl = models.CharField(verbose_name="URL del logo de la compañía", null=True, blank=True)
    url = models.CharField(max_length=100, verbose_name="URL de la compañía", null=True, blank=True)
    desc = models.TextField(verbose_name="Descripción de la compañía", null=True, blank=True)
    direccion = models.ForeignKey(Address, on_delete=models.CASCADE, verbose_name="Dirección de la compañía")
    
    
    class Meta:
        verbose_name="Compañía"
        verbose_name_plural="Compañías"

    def __str__(self):
        return self.nombre