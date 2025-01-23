import cv2
from django.shortcuts import render, redirect
from .forms import FuncionarioForm, ColetaFacesForm
from .models import Funcionario, ColetaFaces
from django.http import StreamingHttpResponse
from .camera import VideoCamera

camera_detection = VideoCamera() #instancia da classe VideoCamera 

#Captura o frame com face detectada
def gen_detect_face(camera):
     while True:
        # Obtem o frame da câmera como bytes
        frame = camera_detection.detect_face()
        # Se o frame estiver vazio, pule a iteração
        if frame is None:
            continue
        
        # Monta o streaming HTTP com os bytes do frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        
#cria streming para detecção facial
def face_detection(request):
    return StreamingHttpResponse(gen_detect_face(camera_detection),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


def criar_funcionario(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, request.FILES)
        if form.is_valid():
            funcionario = form.save()
            return redirect('criar_coleta_faces', funcionario_id=funcionario.id)  # Redireciona para outra página
    else:
        form = FuncionarioForm()  # Inicializa o formulário vazio para GET
    
    # Renderiza a página com o formulário (sempre retorna um HttpResponse)
    return render(request, 'criar_funcionario.html', {'form': form})
    
    

def criar_coleta_faces(request, funcionario_id):
    print(funcionario_id)  # Identifica o funcionário cadastrado
    funcionario = Funcionario.objects.get(id=funcionario_id)  # Resgata o funcionário
    
    camera_detection = VideoCamera()

    # Corrige a captura do botão clicado
    botao_clicado = request.POST.get('cliked', 'False') == 'True'

    context = {
        'funcionario': funcionario,  # Passa o objeto funcionário para o template
        'face_detection': '/face_detection',  # A URL que lida com o streaming da câmera
        'valor_botao': botao_clicado,
    }

    if botao_clicado:
        print("Cliquei em Extrair Imagens !")
        context = face_extract(context, funcionario,camera_detection)  # Chama função de extrair imagem

    return render(request, 'criar_coleta_faces.html', context)

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

            