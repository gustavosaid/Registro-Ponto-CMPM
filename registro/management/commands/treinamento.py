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

        # Processa cada imagem em ColetaFaces
        for coleta in ColetaFaces.objects.all():
            image_path = os.path.join(settings.MEDIA_ROOT, coleta.image.name)

            if not os.path.exists(image_path):
                print(f"Caminho não encontrado: {image_path}")
                erro_count += 1
                continue

            # Carrega e processa a imagem
            image = cv2.imread(image_path)
            if image is None:
                print(f"Erro ao carregar a imagem: {image_path}")
                erro_count += 1
                continue

            imagemFace = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            imagemFace = cv2.resize(imagemFace, (220, 220))
            faces.append(imagemFace)
            labels.append(coleta.funcionario.id)  # ID do funcionário

            # Exibe a data e hora da coleta
            print(f"Imagem processada: {coleta.image.name} | Criada em: {coleta.created_at}")

        # Se não houver faces, interrompe o treinamento
        if not faces:
            print("Nenhuma face encontrada para treinamento")
            return

        # Realiza o treinamento do modelo
        try:
            eigenFace.train(np.array(faces), np.array(labels))
            print(f"{len(faces)} imagens treinadas com sucesso.")

            # Salva o modelo treinado em um arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
                model_filename = tmpfile.name
                eigenFace.write(model_filename)

            # Salva o modelo no banco de dados
            with open(model_filename, 'rb') as f:
                treinamento, _ = Treinamento.objects.get_or_create()
                treinamento.modelo.save('classificadorEigen.yml', File(f))

            # Remove o arquivo temporário
            os.remove(model_filename)

            # Remove as imagens processadas
            for coleta in ColetaFaces.objects.all():
                image_path = os.path.join(settings.MEDIA_ROOT, coleta.image.name)
                if 'treinamento' in coleta.image.name:  # Condição fictícia para imagens usadas no treinamento
                    os.remove(image_path)  # Apaga a imagem
                    print(f"Imagem removida: {image_path}")
            else:
                print(f"Imagem de ROI mantida: {image_path}")

            # Mensagens de status
            self.stdout.write(self.style.ERROR(f"Imagens com erro de carregamento: {erro_count}"))
            self.stdout.write(self.style.SUCCESS("TREINAMENTO EFETUADO"))

        except Exception as e:
            print(f"Erro durante o treinamento ou limpeza dos arquivos: {e}")
