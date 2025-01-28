from django import forms
from .models import Funcionario, ColetaFaces
from django.utils import timezone

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = ['foto', 'nome', 'cpf',]
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Digite seu nome completo'}),
            'cpf': forms.TextInput(attrs={'placeholder': 'Digite seu CPF'}),
            
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            # Se a instância (funcionário) já existir, preenche a foto com o valor atual
            self.fields['foto'].required = False  # Torna a foto opcional
        
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
    def clean_foto(self):
        
        # Caso não tenha sido selecionada uma nova foto, mantemos a foto anterior
        if not self.cleaned_data.get('foto'):
            # Mantém a foto existente
            return self.instance.foto  # Retorna a foto atual do funcionário
        return self.cleaned_data.get('foto')  # Retorna a foto inserida pelo usuário
            
           

    # Validação do CPF
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')  # Acessando corretamente o CPF

        # Verifica se o CPF tem exatamente 11 caracteres
        if len(cpf) != 11:
            raise forms.ValidationError("O CPF deve ter exatamente 11 caracteres.")

        funcionario = Funcionario.objects.filter(cpf=cpf).first()  # Busca o funcionário pelo CPF
        
        # Verifica se já existe um funcionário com o CPF fornecido
        if funcionario:
            # Se o funcionário já está cadastrado, preenche o formulário com seus dados
            self.instance = funcionario  # Atribui a instância do funcionário ao formulário

            # Preenche os campos do formulário com os dados do funcionário
            self.initial['nome'] = funcionario.nome
            self.initial['foto'] = funcionario.foto

        return cpf  # Retorna o CPF validado

    def save(self, commit=True):
        """
        Sobrescreve o método save para definir a data e hora da modificação automaticamente.
        """
        instance = super().save(commit=False)
        instance.dataHora = timezone.now()
        if commit:
            instance.save()
        return instance
    
    def editar_funcionario(request, cpf):
        funcionario = get_object_or_404(Funcionario, cpf=cpf)  # Encontra o funcionário pelo CPF
        form = FuncionarioForm(request.POST or None, instance=funcionario)

        if form.is_valid():
            form.save()
        return redirect('criar_coleta_faces')  # Redireciona para onde quiser

        return render(request, 'criar_coleta_faces.html', {'form': form})

# Multiplos arquivos
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

class ColetaFacesForm(forms.ModelForm):
    images = MultipleFileField()

    class Meta:
        model = ColetaFaces
        fields = ['images']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Não permite a edição da foto já cadastrada no funcionário
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
