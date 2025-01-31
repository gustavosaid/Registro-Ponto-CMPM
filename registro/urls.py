from django.urls import path
from .views import criar_funcionario, criar_coleta_faces, face_detection, buscar_funcionario, botton_buscaFuncionario

urlpatterns = [
    path('', criar_funcionario, name='criar_funcionario'),
    path('criar_coleta_faces/<int:funcionario_id>', criar_coleta_faces, name='criar_coleta_faces'),
    path('face_detection/', face_detection, name='face_detection'),
    path('buscar_funcionario/',buscar_funcionario, name='buscar_funcionario'),
    path('botton_buscaFuncionario/',botton_buscaFuncionario, name='botton_buscaFuncionario'),
    
    
]

