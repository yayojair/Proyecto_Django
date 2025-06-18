from django.urls import path
from .views import *


urlpatterns = [
    path('login/', login_doctor, name='login'),
    path('', index, name='home'),
    path('logout/', logout_doctor, name='logout'),
    path('registro-paciente/', registro_paciente, name='registro-paciente'),
    path('listar-pacientes/', listar_pacientes, name='listar-pacientes'),
    path('actualizar-paciente/', actualizar_paciente, name='actualizar-paciente'),
    path('eliminar-paciente/', eliminacion_logica_paciente, name='eliminar-paciente'),
    path('detalle-paciente/<int:paciente_id>/', detalle_paciente, name='detalle-paciente'),
    path('nueva-consulta/<int:paciente_id>/', nueva_consulta, name='nueva-consulta'),
]