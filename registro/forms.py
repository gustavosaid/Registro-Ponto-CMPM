from django import forms
from .models import Funcionario, ColetaFaces
from django.utils import timezone
from django.core.exceptions import ValidationError
from .utils import validar_cpf # Importa a função de validação de CPF
import re

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = ['nome', 'cpf','observacao']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Digite seu nome completo.'}),
            'cpf': forms.TextInput(attrs={'placeholder': 'Digite seu CPF.'}),
            'observacao': forms.TextInput(attrs={'placeholder': 'Digite o destino.'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
    def clean_observacao(self):
        return self.cleaned_data['observacao'].lower()
    
    #Validação do CPF
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')  # Acessando corretamente o CPF

        # Remover caracteres não numéricos
        cpf = re.sub(r'\D', '', cpf)

        # Verifica se já existe um funcionário com esse CPF
        if Funcionario.objects.filter(cpf=cpf).exists():
            raise ValidationError("Funcionário já cadastrado com este CPF.")

        # Verifica se o CPF é válido
        if not validar_cpf(cpf):
            raise ValidationError("CPF inválido. Digite um CPF válido.")
        return cpf


    def save(self, commit=True):
    #     Sobrescreve o método save para definir a data e hora da modificação automaticamente.
        instance = super().save(commit=False)
        instance.dataHora = timezone.now()
        if commit:
            instance.save()
        return instance

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
        
        #Não permite a edição da foto já cadastrada no funcionário
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            