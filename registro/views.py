import base64
import json
import cv2
import os 
import re
import time 
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, JsonResponse
import numpy as np
from .forms import FuncionarioForm
from .models import Funcionario, ColetaFaces
from .camera import VideoCamera
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.db.models import Q
import hashlib


# Instância da câmera global para detecção facial
camera_detection = VideoCamera()

# Função para capturar o frame com a face detectada
def gen_detect_face(camera):
    while True:
        frame = camera.detect_face()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            print("Frame não detectado. Ignorando...")

# Endpoint Streaming para detecção facial
def face_detection(request):
    return StreamingHttpResponse(
        gen_detect_face(camera_detection),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

# Criação de funcionário e redireciona para a coleta de faces
def criar_funcionario(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, request.FILES) # Formulário de funcionário
        if form.is_valid():
            funcionario = form.save() #salva no banco de dados
            return redirect('criar_coleta_faces', funcionario_id=funcionario.id)
    else:
        form = FuncionarioForm() 

    return render(request, 'criar_funcionario.html', {'form': form})

# Função de extração de imagens das face detectada
def extract(camera_detection, funcionario_slug):
    amostra = 0
    numero_amostras = 1 #nº de imagens a serem coletadas
    largura, altura = 280, 280 #dimensao da imagem
    file_paths = [] #lista onde sera armazenado os caminhos das imagens
    max_falhas = 5
    falhas_consecutivas = 0

    while amostra < numero_amostras:
        ret, frame = camera_detection.get_frame() #captura um frame da camera

        if not ret or frame is None:  # Verifica se o frame foi capturado corretamente
            falhas_consecutivas += 1
            print(f"Falha ao capturar o frame. Tentativa {falhas_consecutivas} de {max_falhas}.")
            
            if falhas_consecutivas >= max_falhas:
                print("Erro: Número máximo de falhas consecutivas atingido. Interrompendo o processo.")
                return []  # Retorna uma lista vazia se falhar várias vezes
            
            continue 
        
        crop = camera_detection.sample_faces(frame) # Recorta a face do frame

        # Verifica se a face foi detectada corretamente
        if crop is not None:
            falhas_consecutivas = 0
            amostra += 1
            
            face = cv2.resize(crop, (largura, altura)) #redimensiona a imagem
            imagemCinza = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)  #converte para cinza
            
            # Caminho para salvar a imagem
            file_name_path = f'./tmp/{funcionario_slug}_{amostra}.jpg'
            cv2.imwrite(file_name_path, imagemCinza) #salva a foto
            file_paths.append(file_name_path)
        else:
            print("Face não encontrada")

    camera_detection.restart()  # Reinicia a câmera após captura
    return file_paths


# API para upload de imagem base64
@csrf_exempt
def upload_image(request):
    if request.method == "POST":
        try:
            # Obtém os dados da requisição
            data = json.loads(request.body)
            image_data = data.get("image")  # A imagem em formato Base64
            funcionario_id = request.GET.get("funcionario_id")  # ID do funcionário
            observacao = request.GET.get("observacao")  # Observação fornecida

            # Verifica se os dados essenciais estão presentes
            if not image_data or not funcionario_id:
                return JsonResponse({"success": False, "error": "Dados inválidos."}, status=400)

            # Busca o funcionário no banco de dados
            try:
                funcionario = Funcionario.objects.get(id=funcionario_id)
            except Funcionario.DoesNotExist:
                return JsonResponse({"success": False, "error": "Funcionário não encontrado."}, status=404)
            
            # Verifica se o número de coletas atingiu o limite de 25
            num_coletas = ColetaFaces.objects.filter(funcionario=funcionario).count()
            if num_coletas >= 50: #limite de fotos tiradas 
                # Retorna erro se o limite de coletas for atingido
                return JsonResponse({"success": False, "error": "Limite máximo de 50 fotos atingidas."}, status=400)

            # Decodifica a imagem Base64
            format, imgstr = image_data.split(";base64,")
            img_data = base64.b64decode(imgstr)

            # Criação do objeto ColetaFaces
            coleta_face = ColetaFaces.objects.create(funcionario=funcionario)

            # Criação do nome do arquivo de imagem baseado no número de coletas já existentes
            file_name = f"{funcionario.slug}_{num_coletas + 1}.jpg"
            coleta_face.image.save(file_name, ContentFile(img_data), save=True)

            # Armazenar a observação no objeto ColetaFaces
            coleta_face.observacao = observacao
            coleta_face.save()

            # URL que deposi que imagem for salva, ridericona para pagina principal
            redirect_url = "/acesso_pessoal"  

            return JsonResponse({"success": True, "redirect_url": redirect_url})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Método inválido."}, status=400)

        

#gerenciar a coleta de face do funcionario
def criar_coleta_faces(request, funcionario_id):
    print(funcionario_id) #id do funcionario cadastrado
    funcionario = Funcionario.objects.get(id=funcionario_id)
    
    # Recebe a observação, se estiver no request
    observacao = request.GET.get('observacao', funcionario.observacao)
    

    if request.method == 'POST':
        # Pega o valor de observação do POST, caso não tenha, mantém o valor atual
        observacao = request.POST.get('observacao', funcionario.observacao)  # Se não houver observação no POST, usa a atual
        
        # Atualiza o campo observação do funcionário
        funcionario.observacao = observacao
        funcionario.save()  # Salva no banco de dados
        
    else:
        # Se for GET, usamos a observação que já está no banco
        observacao = funcionario.observacao
    context = {
        'funcionario': funcionario,
        'face_detection': face_detection,
        'observacao': observacao,  # Passa a observação para o template
    }


    return render(request, 'criar_coleta_faces.html', context)


#busca funcionario pelo cpf
def buscar_funcionario(request):
    # Obtém o CPF da URL e remove espaços extras
    nome = request.GET.get('nome', '').strip()
    cpf = request.GET.get('cpf', '').strip()

    cpf_hash = hashlib.sha256(cpf.encode()).hexdigest()

    funcionario = Funcionario.objects.filter(Q(nome=nome) | Q(cpf_hash=cpf_hash)).first()

    if funcionario:
        return redirect('criar_coleta_faces', funcionario_id=funcionario.id)

    return redirect('criar_funcionario')


#pagina para encontrar funcionario
def encontra_funcionario(request):
    return render(request,'encontra_funcionario.html')

# def custom_404(request,exception=None):
#     return render(request, '404.html', status=404)