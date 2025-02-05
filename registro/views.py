import cv2
import os 
import re
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse
from .forms import FuncionarioForm
from .models import Funcionario, ColetaFaces
from .camera import VideoCamera
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

# Instância da câmera global
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
    numero_amostras = 1
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
    
    print(num_coletas) # quantidade de imagens que o funcionario tem cadastrado

    
    if num_coletas >= 50: #verifica se limite de coletas foi atingido
        context['erro'] = 'Limite máximo de coletas atingido.'
    else:
            # Extrair as faces usando o método da câmera
        file_paths = extract(camera_detection, funcionario.slug)
        print(file_paths)#path rostos
        
        for path in file_paths:
            # Cria uma instância de ColetaFaces e salva a imagem
            coleta_face = ColetaFaces.objects.create(funcionario=funcionario)
            coleta_face.image.save(os.path.basename(path), open(path, 'rb'))
            coleta_face.observacao = funcionario.observacao  # Adiciona a observação
            coleta_face.save()  # Salva a coleta com a observação
            os.remove(path)  # Remove o arquivo temporário após salvamento
        
        #atualiza o contexto com coletas salvas
        context['file_paths'] = ColetaFaces.objects.filter(
            funcionario__slug=funcionario.slug)
        context['extracao_ok'] = True #Define sinalizador de sucesso

    return context
        

# Criação de coletas de faces
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

    botao_clicado = request.POST.get("cliked", "False") == "True"
    
    if botao_clicado:
        print("Cliquei em Extrair Imagens!")
        context = face_extract(context, funcionario)  # Chama função para extrair funcionário

    return render(request, 'criar_coleta_faces.html', context)


# def validar_cpf(cpf):
#     """ Valida se o CPF tem 11 dígitos numéricos """
#     return bool(re.fullmatch(r'\d{11}', cpf))

def buscar_funcionario(request):
    # Obtém o CPF da URL e remove espaços extras
    cpf = request.GET.get('cpf', '').strip()

    # Validação do CPF: deve conter exatamente 11 números
    # if not validar_cpf(cpf):
    #     return redirect('criar_funcionario')

    # Busca funcionário no banco de dados
    funcionario = Funcionario.objects.filter(cpf=cpf).first()

    if funcionario:
        # Se o CPF já estiver cadastrado, redireciona para a página de coleta de faces
        return redirect('criar_coleta_faces', funcionario_id=funcionario.id)

    # Se não encontrou o funcionário, direciona para o cadastro
    return redirect('criar_funcionario')

def encontra_funcionario(request):
    return render(request,'encontra_funcionario.html')
    # cpf = self.cleaned_data.get('cpf')  # Acessando corretamente o CPF
    
    

