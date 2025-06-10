from django.db import models
from MainApp.models import Address

# --- Modelos compartidos ---

class TipoMedioPago(models.TextChoices):
    TARJETA_CREDITO = 'TC', 'Tarjeta de Crédito'
    TRANSFERENCIA_BANCARIA = 'TB', 'Transferencia Bancaria'

class MedioPago(models.Model):
    tipo = models.CharField(max_length=2, choices=TipoMedioPago.choices)
    Cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, related_name='medios_pago')

    def __str__(self):
        return f"{self.tipo}"

class TarjetaCredito(MedioPago):
    tarjeta = models.CharField(max_length=30) # Visa, Mastercard, etc.
    numero_tarjeta = models.CharField(max_length=20)
    titular = models.CharField(max_length=100)
    vencimiento = models.CharField(max_length=5)  # Formato MM/AA

    def __str__(self):
        return f"{self.tarjeta} - {self.numero_tarjeta}"
    
    def vencida(self):
        from datetime import datetime
        hoy = datetime.now()
        mes, anio = map(int, self.vencimiento.split('/'))
        vencimiento = datetime((anio + 2000) + (mes // 12), mes % 12 + 1, 1)
        return hoy > vencimiento

class TransferenciaBancaria(MedioPago):
    cbu = models.CharField(max_length=20)
    titular_cuenta = models.CharField(max_length=100)

    def __str__(self):
        return f"CBU: {self.cbu}"
    
class CondicionIVA(models.TextChoices):
    RESPONSABLE_INSCRIPTO = 'RI', 'Responsable Inscripto'
    MONOTRIBUTO = 'MO', 'Monotributo'
    EXENTO = 'EX', 'Exento'
    NO_RESPONSABLE = 'NR', 'No Responsable'
    CONSUMIDOR_FINAL = 'CF', 'Consumidor Final'


class TelefonoCte(models.Model):
    numero = models.CharField(max_length=20)
    contacto = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.numero} - {self.contacto} - {self.descripcion}"

class EmailCte(models.Model):
    email = models.EmailField()
    contacto = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.email} - {self.contacto} - {self.descripcion}"


# --- Cliente base ---

class Cliente(models.Model):
    condicion_iva = models.CharField(max_length=2, choices=CondicionIVA.choices)
    direccion = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    telefonos = models.ManyToManyField(TelefonoCte, blank=True)
    emails = models.ManyToManyField(EmailCte, blank=True)
    notas = models.TextField(blank=True)

    class Meta:
        abstract = False

    def __str__(self):
        return f"Cliente #{self.id}"


# --- Persona Física ---

class ClientePersonaFisica(Cliente):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20)
    fecha_nacimiento = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"


# --- Persona Jurídica ---

class ClientePersonaJuridica(Cliente):
    razon_social = models.CharField(max_length=100)
    cuit = models.CharField(max_length=20)

    def __str__(self):
        return self.razon_social
