import cv2
import os

class VideoCamera(object):
    def __init__(self):
        # Abre a câmera
        self.face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        self.video = cv2.VideoCapture(0)  # Abre a câmera do PC

        if not self.video.isOpened():
            print("Erro ao abrir a câmera.")# Verifica se a câmera foi aberta corretamente
            
        self.img_dir = "./tmp" #pasta auxiliar 
        
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir) #Cria a pasta 'tmp' se nao existir

    def __del__(self):
        self.video.release() # Libera a câmera ao destruir a classe

    def restart(self):
        self.video.release()  # Reinicia a câmera
        self.video = cv2.VideoCapture(0)

    # Retorna o frame no modo normal do objeto
    def get_frame(self):
        # Lê o frame da câmera
        ret, frame = self.video.read()
        if not ret:
            print("Falha ao capturar o frame.")  # Verifica se a captura do frame foi bem-sucedida
            return ret, frame
        
        # Converte o frame em imagem JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            print("Erro ao codificar o frame para JPEG.")  # Verifica se a codificação foi bem-sucedida
            return None, None
        
        return ret, jpeg.tobytes()

    def detect_face(self):
        # Lê o frame da câmera
        ret, frame = self.video.read() 
        if not ret:
            print("Falha ao capturar o frame.")  # Verifica se a captura do frame foi bem-sucedida
            return None
        
        #Define a regiao de interesse (ROI) onde o rosto sera detectado
        altura, largura, _ = frame.shape  # Obtém a altura e largura do frame
        centro_x, centro_y = int(largura/2), int(altura/2)  # Calcula o centro do frame
        a, b = 140, 180  # Define os valores de a e b (provavelmente para definir uma região de interesse)
        x1, y1 = centro_x - a, centro_y - b  # Calcula o canto superior esquerdo da região de interesse
        x2, y2 = centro_x + a, centro_y + b  # Calcula o canto inferior direito da região de interesse
        roi = frame[y1:y2, x1:x2]  # Cria a região de interesse (ROI)
        
        # Converte para escala de cinza para melhorar a detecção de faces
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detecta faces no frame
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        cv2.ellipse(frame,(centro_x,centro_y), (a,b), 0, 0, 360, (0, 0, 255),10) #elipse vermelha
        
        
        
        # Desenha um retângulo em torno das faces detectadas
        for (x, y, w, h) in faces:
            cv2.ellipse(frame,(centro_x,centro_y), (a,b), 0, 0, 360, (0, 255,0 ),10)  #elipese verde
        
        # Retorna o frame com as faces detectadas, no formato JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
    
    def sample_faces(self, frame):
        if frame is None:
            print("Frame inválido recebido. Abortando detecção.")
            return None

        # frame = cv2.flip(frame, 0)  # Inverte horizontalmente, ajuste conforme necessário
        # frame = cv2.resize(frame, (480, 360))  # Redimensiona o frame

        # Detecta as faces no frame
        faces = self.face_cascade.detectMultiScale(
            frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), maxSize=(400, 400)
        )

        if len(faces) == 0:
            print("Nenhuma face encontrada.")
            return None

        for (x, y, w, h) in faces:
            cropped_face = frame[y:y + h, x:x + w]
            return cropped_face  # Retorna apenas a primeira face encontrada

        return None
        