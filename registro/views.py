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
        frame = camera.detect_face()
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
            
            # Caminho para salvar a imagem
            file_name_path = f'./tmp/{funcionario_slug}_{amostra}.jpg'
            cv2.imwrite(file_name_path, imagemCinza)
            file_paths.append(file_name_path)
        else:
            print("Face não encontrada")

    camera_detection.restart()  # Reinicia a câmera após captura
    return file_paths

# Função principal de extração
def face_extract(context, funcionario):
    num_coletas = ColetaFaces.objects.filter(
        funcionario__slug=funcionario.slug).count()
    
    print(num_coletas)
    
    context = {}
    
    if num_coletas >= 10:
        context['error'] = 'Limite máximo de coletas atingido.'
    else:
            # Extrair as faces usando o método da câmera
            file_paths = extract(camera_detection, funcionario.slug)
            print(file_paths)
    return context

# Criação de coletas de faces
def criar_coleta_faces(request, funcionario_id):
    funcionario = Funcionario.objects.get(id=funcionario_id)
    
    botao_clicado = request.POST.get("cliked", "False") == "True"
    
    context = {
        'funcionario': funcionario,
        'face_detection': face_detection,
    }

    if botao_clicado:
        print("Cliquei em Extrair Imagens!")
        # camera_detection = VideoCamera()
        context = face_extract(context, funcionario)  # Chama função para extrair funcionário

    return render(request, 'criar_coleta_faces.html', context)
