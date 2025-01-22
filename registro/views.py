from django.shortcuts import render, redirect
from .forms import FuncionarioForm, ColetaFacesForm
from .models import Funcionario, ColetaFaces
from django.http import StreamingHttpResponse
from .camera import VideoCamera

camera_detection = VideoCamera() #instancia da classe VideoCamera 

#Captura o frame com face detectada
def gen(camera):
    while True:
        frame = camera.get_camera()
        if frame:
            break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        
        
#cria streming para detecção facial
def face_detection(request):
    return StreamingHttpResponse(gen(VideoCamera()),
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
    print(funcionario_id) #identificador o funcionario cadastrado
    funcionario = Funcionario.objects.get(id=funcionario_id) #resgata funcionario
    
    context = {
        'funcionario': funcionario, #passa o objeto funcionario para o template
        'face_detection' : face_detection, #pass a camera para renderizar no template
        #'data_hora': data_hora_atual.strftime('%d/%m/%Y %H:%M:%S'),
    }

    return render (request, 'criar_coleta_faces.html', context)