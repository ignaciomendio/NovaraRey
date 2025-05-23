from django.db import models

class CiaTelContact(models.Model):
    telefono = models.CharField(max_length=50, verbose_name="Teléfono")
    contacto = models.CharField(max_length=50, verbose_name="Contacto")
    desc = models.CharField(max_length=100, verbose_name="Descripción del contacto", null=True, blank=True)

    
    class Meta:
        verbose_name="teléfono de Contacto"
        verbose_name_plural="Teléfonos de contacto"

    def __str__(self):
        return "tel:" + self.telefono + " - " + self.contacto
    

class CiaMailContact(models.Model):
    mail = models.EmailField(max_length=50, verbose_name="Mail")
    contacto = models.CharField(max_length=50, verbose_name="Contacto")
    desc = models.CharField(max_length=100, verbose_name="Descripción del contacto", null=True, blank=True)

    
    class Meta:
        verbose_name="mail de Contacto"
        verbose_name_plural="Mails de contacto"

    def __str__(self):
        return "E-Mail:" + self.mail + " - " + self.contacto
    
class Cia(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre de la compañía")
    logoUrl = models.CharField(verbose_name="URL del logo de la compañía", null=True, blank=True)
    cuit = models.CharField(max_length=15, verbose_name="CUIT de la compañía")
    desc = models.TextField(verbose_name="Descripción de la compañía", null=True, blank=True)

    
    class Meta:
        verbose_name="Compañía"
        verbose_name_plural="Compañías"

    def __str__(self):
        return self.nombre