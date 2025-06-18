from django.db import models
from django.contrib.auth.models import User 

# Modelo que representa a un Doctor en el sistema
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=50)  # Nombre del doctor
    apellido = models.CharField(max_length=50)  # Apellido del doctor
    edad = models.IntegerField()  # Edad del doctor
    sexo = models.CharField(max_length=7)  # Sexo del doctor (puede ser 'masculino', 'femenino', etc.)

    def __str__(self):
        # Representación legible del doctor (útil en el admin de Django)
        return f"{self.nombre} {self.apellido}"

# Modelo que representa un Síntoma posible durante una consulta
class Sintoma(models.Model):
    nombre = models.CharField(max_length=100)  # Nombre del síntoma (ej. "Fiebre", "Dolor de cabeza")

    def __str__(self):
        return self.nombre

# Modelo que representa un Medicamento que puede recetarse durante una consulta
class Medicamento(models.Model):
    nombre = models.CharField(max_length=100)  # Nombre del medicamento (ej. "Paracetamol")

    def __str__(self):
        return self.nombre

# Modelo que representa a un Paciente del sistema
class Paciente(models.Model):
    nombre = models.CharField(max_length=50)  # Nombre del paciente
    apellido = models.CharField(max_length=50)  # Apellido del paciente
    edad = models.IntegerField()  # Edad del paciente
    sexo = models.CharField(max_length=7)  # Sexo del paciente
    estado = models.CharField(max_length=9, default='activo')  # Estado del paciente (activo, inactivo, etc.)

    # Relación muchos a muchos: un paciente puede tener varios doctores y un doctor varios pacientes
    doctor = models.ManyToManyField(Doctor, related_name='pacientes')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# Modelo que representa una Consulta médica realizada a un paciente
class Consulta(models.Model):
    observacion = models.CharField(max_length=100)  # Observaciones generales de la consulta (motivo, diagnóstico breve)
    peso = models.IntegerField()  # Peso del paciente en el momento de la consulta
    fecha = models.DateTimeField()  # Fecha de la consulta (se asigna automáticamente al crearla)

    # Relación muchos a muchos con síntomas: una consulta puede tener múltiples síntomas asociados
    sintoma = models.ManyToManyField(Sintoma, related_name='consultas')

    # Relación muchos a muchos con medicamentos: una consulta puede incluir múltiples medicamentos
    medicamento = models.ManyToManyField(Medicamento, related_name='consultas')

    # Relación muchos a uno: una consulta pertenece a un solo paciente
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='consultas')

    # Relación muchos a uno: una consulta fue realizada por un solo doctor
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='consultas')

    def __str__(self):
        # Representación legible de la consulta, indicando paciente, doctor y fecha
        return f"Consulta de {self.paciente} con {self.doctor} en {self.fecha.strftime('%Y-%m-%d')}"
