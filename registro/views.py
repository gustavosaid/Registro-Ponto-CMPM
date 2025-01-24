import cv2
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse
from .forms import FuncionarioForm
from .models import Funcionario, ColetaFaces
from .camera import VideoCamera

# Instância da câmera global
camera_detection = VideoCamera()

# Função para capturar o frame com a face detectada
def gen_detect_face(camera):
    while True:
        frame = camera_detection.detect_face()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# Streaming para detecção facial
def face_detection(request):
    return StreamingHttpResponse(
        gen_detect_face(camera_detection),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )


# Criação de funcionário
def criar_funcionario(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, request.FILES)
        if form.is_valid():
            funcionario = form.save()
            return redirect('criar_coleta_faces', funcionario_id=funcionario.id)
    else:
        form = FuncionarioForm()
        
    return render(request, 'criar_funcionario.html', {'form': form})


# Função de extração de imagens e retornar o file_path
def extract(camera_detection, funcionario_slug):
    amostra = 0
    numero_amostras = 5
    largura, altura = 280, 280
    file_paths = []
    max_falhas = 10
    falhas_consecutivas = 0

    while amostra < numero_amostras:
        ret, frame = camera_detection.get_frame()

        if not ret or frame is None:  # Verifica se o frame foi capturado corretamente
            falhas_consecutivas += 1
            print(f"Falha ao capturar o frame. Tentativa {falhas_consecutivas} de {max_falhas}.")
            
            if falhas_consecutivas >= max_falhas:
                print("Erro: Número máximo de falhas consecutivas atingido. Interrompendo o processo.")
                return []  # Retorna uma lista vazia se falhar várias vezes
            
            continue
        
        crop = camera_detection.sample_faces(frame)

        # Verifica se a face foi detectada corretamente
        if crop is not None:
            falhas_consecutivas = 0
            amostra += 1
            
            face = cv2.resize(crop, (largura, altura))
            imagemCinza = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            
            
            #caminho para salvar a imagem
            file_name_path = f'./tmp/{funcionario_slug}_{amostra}.jpg'
            cv2.imwrite(file_name_path, imagemCinza)
            file_paths.append(file_name_path)
        else:
            print("Face nao encontrada")

    camera_detection.restart() #reinia camera apos captura
    return file_paths


# Função principal de extração
def face_extract(funcionario, camera_detection):
    num_coletas = ColetaFaces.objects.filter(
        funcionario__slug=funcionario.slug).count()
    
    print(num_coletas)
    
    context = {}
    
    if num_coletas >= 10:
        context['error'] = 'Limite máximo de coletas atingido.'
    else:
        try:
            # Extrair as faces usando o método da câmera
            file_paths = extract(camera_detection, funcionario.slug)
            print(f"Arquivos extraídos: {file_paths}")
            context['file_paths'] = file_paths
        except Exception as e:
            # Caso haja erro ao extrair as imagens
            print(f"Erro ao extrair as imagens: {e}")
            context['error'] = 'Erro ao extrair as imagens.'

    return context       


# Criação de coletas de faces
def criar_coleta_faces(request, funcionario_id):
    
    funcionario = Funcionario.objects.get(id=funcionario_id)
    
    botao_clicado = request.POST.get("cliked", "False") == "True"
    
    context = {
        'funcionario': funcionario,
        'face_detection': '/face_detection',
    }

    if botao_clicado:
        print("Cliquei em Extrair Imagens!")
        camera_detection = VideoCamera()
        context = face_extract(funcionario, camera_detection) #chama funcao para extrair funcionario

    return render(request, 'criar_coleta_faces.html', context)
<<<<<<< HEAD
=======

def face_extract(context, funcionario,camera_detection):
    num_coletas = ColetaFaces.objects.filter(
        funcionario__slug=funcionario.slug).count()

    print(num_coletas)  # Quantidade de imagens que o usuário já cadastrou.

    if num_coletas >= 10:
        context['error'] = 'Limite máximo de coletas atingido.'
        return context

    amostra = 0  # Amostra inicial
    numeroAmostras = 3  # Número de amostras para extrair
    largura, altura = 240, 240  # Dimensão da face (quadrada)
    file_paths = []  # Lista de caminhos das amostras

    while amostra < numeroAmostras:  # Loop para capturar 10 amostras
        ret, frame = camera_detection.get_frame()  # Captura o frame da câmera

        # Verifica se o frame foi capturado corretamente
        if not ret or frame is None:
            print("Falha ao capturar o frame. Tentando novamente...")
            continue  # Passa para a próxima iteração do loop

        crop = camera_detection.sample_faces(frame)  # Captura a face no frame

        if crop is not None:  # Se uma face for detectada
            amostra += 1  # Incrementa o contador de amostras

            # Redimensiona e converte a face para tons de cinza
            face = cv2.resize(crop, (largura, altura))
            imagemCinza = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

            # Define o caminho para salvar a imagem
            file_name_path = f'./tmp/{funcionario.slug}_{amostra}.jpg'
            print(f"Salvando imagem: {file_name_path}")

            cv2.imwrite(file_name_path, imagemCinza)  # Salva a imagem
            file_paths.append(file_name_path)  # Adiciona à lista de caminhos
        else:
            print("Nenhuma face detectada no frame atual.")

        if amostra >= numeroAmostras:
            break  # Encerra o loop após atingir o número de amostras desejado

    camera_detection.restart()  # Reinicia a câmera após as capturas

    print(f"Arquivos salvos: {file_paths}")
    return context

            
>>>>>>> origin/main
