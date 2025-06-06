from django.urls import path
from .views import *


urlpatterns = [
    path('', Index, name='home'),
    path('login/', login_usuarios, name='login'),
    path('logout/', logout_admin, name='logout'),
    path('registro-paciente/', registro_paciente, name='registro-paciente'),
    path('listar-pacientes/', listar_pacientes, name='listar-pacientes'),
    path('actualizar-paciente/', actualizar_paciente, name='actualizar-paciente'),
    path('eliminar-paciente/', elimina_paciente, name='eliminar-paciente'),
]