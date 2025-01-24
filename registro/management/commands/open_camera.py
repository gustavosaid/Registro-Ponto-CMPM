from django.core.management.base import BaseCommand
import cv2

class Command(BaseCommand):
    help = 'Abre a câmera e exibe o vídeo em tempo real'

    def handle(self, *args, **kwargs):
        """
        Abre a câmera padrão e exibe o vídeo em uma janela.

        Args:
            *args: Argumentos posicionais (não utilizados neste caso).
            **kwargs: Argumentos nomeados (não utilizados neste caso).
        """

        # Abre a câmera (0 é o índice padrão)
        cap =  cv2.VideoCapture(0)

        if not cap.isOpened():
            self.stdout.write(self.style.ERROR('Erro ao abrir a câmera'))
            return

        self.stdout.write(self.style.SUCCESS('Câmera aberta com sucesso. Pressione "q" para sair.'))

        while True:
            # Captura um frame
            ret, frame = cap.read()

            if not ret:
                self.stdout.write(self.style.ERROR('Erro ao capturar o frame'))
                break

            # Exibe o frame em uma janela
            cv2.imshow('Camera', frame)

            # Verifica se a tecla 'q' foi pressionada para sair
            if cv2.waitKey(1) == ord('q'):
                break

        # Libera a câmera e fecha a janela
        cap.release()
        cv2.destroyAllWindows()
        self.stdout.write(self.style.SUCCESS('Câmera fechada.'))