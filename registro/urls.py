from django.urls import path
from .views import (criar_funcionario, criar_coleta_faces, face_detection,
                    buscar_funcionario, encontra_funcionario, relatorio_power_bi)

urlpatterns = [
    path('', criar_funcionario, name='criar_funcionario'),
    path('criar_coleta_faces/<int:funcionario_id>', criar_coleta_faces, name='criar_coleta_faces'),
    path('face_detection/', face_detection, name='face_detection'),
    path('buscar_funcionario/',buscar_funcionario, name='buscar_funcionario'),
    path('encontra_funcionario/',encontra_funcionario, name='encontra_funcionario'),
    path('relatorio/',relatorio_power_bi, name='relatorio'),
    
    
]

