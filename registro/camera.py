import cv2
import os
import time

class VideoCamera(object):
    def __init__(self):
        # Abre a câmera
        self.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        if not self.video.isOpened():
            print("Erro: Não foi possível abrir a câmera. Verifique se está conectada.")
            raise Exception("Falha ao acessar a câmera.")

        # Inicializa o classificador de face
        self.face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

        # Diretório para salvar imagens temporárias
        self.img_dir = "./tmp"
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)

    def __del__(self):
        # Libera a câmera ao destruir a classe
        self.video.release()

    def restart(self):
        # Reinicia a câmera
        self.video.release()
        self.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    def get_frame(self):
        # Número máximo de tentativas para capturar o frame
        max_attempts = 10
        attempts = 0

        while attempts < max_attempts:
            ret, frame = self.video.read()
            if ret and frame is not None:
                # Frame capturado com sucesso
                return ret, frame

            attempts += 1
            print(f"Tentativa {attempts} de {max_attempts}: Falha ao capturar o frame.")
            time.sleep(1)  # Aguarda 1 segundo antes de tentar novamente

        # Após várias tentativas, reinicia a câmera e retorna erro
        print("Erro: Timeout ao tentar capturar o frame. Reinicializando a câmera...")
        self.restart()
        return None, None

    def detect_face(self):
        # Lê o frame da câmera
        ret, frame = self.get_frame()
        if not ret or frame is None:
            print("Erro: Não foi possível capturar o frame para detecção de face.")
            return None

        # Obtém as dimensões do frame
        altura, largura, _ = frame.shape
        
        # Define a região de interesse (ROI)
        centro_x, centro_y = int(largura / 2), int(altura / 2)
        a, b = 140, 180
        x1, y1 = centro_x - a, centro_y - b
        x2, y2 = centro_x + a, centro_y + b
        roi = frame[y1:y2, x1:x2]

        # Converte para escala de cinza para detecção
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detecta faces
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        # Desenha elipses no frame
        cv2.ellipse(frame, (centro_x, centro_y), (a, b), 0, 0, 360, (0, 0, 255), 10)
        for (x, y, w, h) in faces:
            cv2.ellipse(frame, (centro_x, centro_y), (a, b), 0, 0, 360, (0, 255, 0), 10)

        # Codifica o frame como JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def sample_faces(self, frame):
        # Verifica se o frame é válido
        if frame is None:
            print("Frame inválido recebido. Abortando detecção.")
            return None

        # Detecta faces no frame
        faces = self.face_cascade.detectMultiScale(
            frame, minNeighbors=20, minSize=(30, 30), maxSize=(400, 400)
        )

        # Retorna a primeira face encontrada
        for (x, y, w, h) in faces:
            cropped_face = frame[y:y + h, x:x + w]
            return cropped_face

        return None
