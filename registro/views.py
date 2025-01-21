from django.shortcuts import render, redirect
from .forms import FuncionarioForm, ColetaFacesForm
from .models import Funcionario, ColetaFaces

def criar_funcionario(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redireciona para outra página
    else:
        form = FuncionarioForm()  # Inicializa o formulário vazio para GET
    
    # Renderiza a página com o formulário (sempre retorna um HttpResponse)
    return render(request, 'registro/criar_funcionario.html', {'form': form})
    
    

def criar_coleta_faces(request, funcionario_id):
    funcionario = Funcionario.objects.get(id=funcionario_id)
    
    if request.method == 'POST':
        form = ColetaFacesForm(request.POST, request.FILES)
        if form.is_valid():
            # Itera sobre os arquivos enviados e cria uma entrada para cada imagem
            for image in request.FILES.getlist('images'):
                ColetaFaces.objects.create(
                    funcionario=funcionario, imagem=image
                )
    else:
        form = ColetaFacesForm()
    
    context = {
        'funcionario': funcionario,
        'form': form
    }

    
    return render (request, 'criar_coleta_faces.html', context)