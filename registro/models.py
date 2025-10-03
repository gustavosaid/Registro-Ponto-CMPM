from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from random import randint
from django.utils.timezone import now  # Para timestamps com timezone-aware
from django_cryptography.fields import encrypt
import hashlib
from encrypted_model_fields.fields import EncryptedCharField


class Funcionario(models.Model):
    slug = models.SlugField(max_length=200, unique=True)
    nome = models.CharField(max_length=50)
    cpf = EncryptedCharField(max_length=11)
    cpf_hash = models.CharField(max_length=64, editable=False, null=True) 
    observacao = models.CharField(max_length=50, blank=True)
    dataHora = models.DateTimeField(default=now) 

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            seq = self.nome + '_FUNC' + str(randint(10000000, 99999999))
            self.slug = slugify(seq)

        # Gera o hash do CPF para buscas
        if self.cpf:
            self.cpf_hash = hashlib.sha256(self.cpf.encode()).hexdigest()

        super().save(*args, **kwargs)


class ColetaFaces(models.Model):
    funcionario = models.ForeignKey(
        Funcionario,  # Referência ao modelo Funcionario
        on_delete=models.CASCADE,
        related_name='funcionario_coletas'
    )
    image = models.ImageField(upload_to='roi')
    criacao = models.DateTimeField(default=now, editable=False)  # Campo para data e hora da criação
    observacao = models.CharField(max_length=50, null=True, blank=True)
    
    def save(self, *args, **kwargs):
            if self.observacao:
                self.observacao = self.observacao.lower()  # Converte para minúsculas antes de salvar
            super().save(*args, **kwargs)
            
    def __str__(self):
        # Evitar recursão: Exibe a hora formatada diretamente
        return f"Coleta de {self.funcionario.nome} em {self.criacao.strftime('%d/%m/%Y %H:%M:%S')} " # caso queria pode colocar aqui - Observação: {self.observacao}
    

class Treinamento(models.Model):
    modelo = models.FileField(upload_to='treinamento/')  # Arquivo .yml

    class Meta:
        verbose_name = 'Treinamento'
        verbose_name_plural = 'Treinamentos'

    def __str__(self):
        return 'Classificador (frontalface)'

    def clean(self):  # Limita a um único arquivo
        model = self.__class__
        if model.objects.exclude(id=self.id).exists():
            raise ValidationError('Só pode haver um arquivo salvo!')
