import os
import numpy as np
import cv2
import tempfile
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from registro.models import ColetaFaces, Treinamento

class Command(BaseCommand):
  help = "Treina o classificador Eigen para reconhecimento facial"

  def handle(self, *args, **kwargs):
    self.treinamento_face()

  def treinamento_face(self):
    self.stdout.write(self.style.WARNING("Iniciando treinamento com a base de informações"))
    print(cv2.__version__)

    # Inicializa o classificador EigenFace
    eigenFace = cv2.face.EigenFaceRecognizer_create(num_components=50, threshold=0)
    
    faces, labels = [], []
    erro_count = 0
    
    #processa cada imagem em ColetaFaces
    for coleta in ColetaFaces.objects.all():
        image_file = coleta.image.url.replace('/media/roi/', '')
        image_path = os.path.join(settings.MEDIA_ROOT, 'roi', image_file)
        
        if not os.path.exists(image_path):
            print(f"Caminho nao encontrado: {image_path}")
            erro_count += 1
            continue
        
        #carrega e processa imagem
        image = cv2.imread(image_path)
        if image is None:
            print(f"Erro ao carregar a imagem: {image_path}")
            erro_count += 1
            continue
        
        imagemFace = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        imagemFace = cv2.resize(imagemFace,(220,220))
        faces.append(imagemFace)
        labels.append(coleta.funcionario.id) #id do funcionario

        
        #se nao foiver faces, interrompe o treinamento
        if not faces:
            print("Nenhuma face encontrada para treinamento")
            return 
        
        #Realiza treinamento do modelo
        try:
            eigenFace.train(np.array(faces), np.array(labels))
            print(f"{len(faces)} imagens treinadas com sucesso.")
            
            #salva modelo treinado em um arquivo temporario
            with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
                model_filename = tmpfile.name
                eigenFace.write(model_filename)
            
            #salva modelo no banco de dados
            with open (model_filename, 'rb') as f:
                treinamento, create = Treinamento.objects.get_or_create()
                treinamento.modelo.save('classificadorEigen.yml', File(f))
                
            try:
            #remove arquivo temporario e exibe mensagem de status
                os.remove(model_filename)
            except Exception as e:
                print(f"Erro ao remover o arquivo temporário: {e}")
                self.stdout.write(self.style.ERROR(f"Erro ao remover o arquivo temporário: {e}"))

            self.stdout.write(self.style.ERROR(f"Imagens com erro de carregamento: {erro_count}"))
            self.stdout.write(self.style.SUCCESS("TREINAMENTO EFETUADO"))