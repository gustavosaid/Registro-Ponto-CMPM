
from django.urls import path
from django.conf.urls import handler404

from .views import (criar_funcionario, criar_coleta_faces, face_detection,
                    buscar_funcionario, encontra_funcionario, upload_image)

urlpatterns = [
    path('acesso_pessoal', criar_funcionario, name='criar_funcionario'),
    path('criar_coleta_faces/<int:funcionario_id>', criar_coleta_faces, name='criar_coleta_faces'),  # rota onde registra nova foto
    path('face_detection/', face_detection, name='face_detection'), # rota camera para detectar foto
    path('buscar_funcionario/',buscar_funcionario, name='buscar_funcionario'), 
    path('encontra_funcionario/',encontra_funcionario, name='encontra_funcionario'), # tela de encontrar pessoa cadastrada
    path('upload_image/', upload_image, name='upload_image'), 
    ]
 