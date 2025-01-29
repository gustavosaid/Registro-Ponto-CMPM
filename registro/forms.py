from django import forms
from .models import Funcionario, ColetaFaces
from django.utils import timezone

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = ['foto', 'nome', 'cpf','observacao']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Digite seu nome completo.'}),
            'cpf': forms.TextInput(attrs={'placeholder': 'Digite seu CPF.'}),
            'observacao': forms.TextInput(attrs={'placeholder': 'Digite a informação.'}),
            
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if not self.instance.pk or not self.instance.foto:
            self.fields['foto'].required = True  # Torna a foto obrigatória se não houver uma imagem
        else:
            self.fields['foto'].required = False  # Permite que a foto seja opcional se já existir
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
            # Se o CPF já estiver cadastrado, preenche os dados do funcionário no formulário
            self.instance = funcionario  # Atribui o funcionário ao formulário
            self.initial['nome'] = funcionario.nome
            self.initial['foto'] = funcionario.foto
            self.initial['observacao'] = funcionario.observacao
            
            # Não permite alteração no nome, foto ou observação
            self.fields['nome'].widget.attrs['readonly'] = True
            self.fields['foto'].widget.attrs['readonly'] = True
            self.fields['observacao'].widget.attrs['readonly'] = True
        return cpf  # Retorna o CPF validado

        return cpf  # Retorna o CPF validado

    def save(self, commit=True):
    #     """
    #     Sobrescreve o método save para definir a data e hora da modificação automaticamente.
    #     """
    
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
        fields = ['images', 'observacao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Não permite a edição da foto já cadastrada no funcionário
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'