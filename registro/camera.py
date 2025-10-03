import cv2
import os
import time

class VideoCamera(object):
    def __init__(self):
        # Inicializa a câmera
        self.video = cv2.VideoCapture(0,cv2.CAP_MSMF)
        # if not self.video.isOpened():
        #     raise Exception("Erro: Não foi possível abrir a câmera. Verifique se está conectada corretamente.")

        # Carrega o classificador Haar para detecção de faces
        cascade_path = "haarcascade_frontalface_default (3).xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
             raise Exception(f"Erro: O classificador Haar Cascade não foi carregado. Verifique o caminho: {cascade_path}")

        # Configura o diretório para salvar imagens temporárias
        self.img_dir = "./tmp"
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)
        print("Câmera inicializada com sucesso e classificador Haar carregado.")

    def __del__(self):
        # Libera a câmera quando o objeto é destruído
        self.video.release()
        print("Câmera liberada.")

    def restart(self):
        # Reinicia a câmera
        print("Reiniciando a câmera...")
        self.video.release()
        time.sleep(2)  # Aguarda 2 segundos antes de reiniciar
        self.video = cv2.VideoCapture(0, cv2.CAP_MSMF)
        if not self.video.isOpened():
            raise Exception("Erro: Não foi possível reiniciar a câmera.")

    def get_frame(self):
        # Tenta capturar o frame com várias tentativas
        max_attempts = 10
        for attempt in range(1, max_attempts + 1):
            ret, frame = self.video.read()
            if ret and frame is not None:
                return ret, frame
            print(f"Falha ao capturar o frame. Tentativa {attempt} de {max_attempts}.")
            time.sleep(1)  # Espera antes de tentar novamente

        # Se falhar após várias tentativas, reinicia a câmera
        print("Erro: Timeout ao capturar o frame. Reinicializando a câmera...")
        self.restart()
        return None, None

    def detect_face(self):
        # Captura o frame da câmera
        ret, frame = self.video.read()
        if not ret or frame is None or frame.size == 0:
            print("Erro: Não foi possível capturar o frame para detecção de face.")
            return None

        # Obtém as dimensões do frame
        altura, largura, _ = frame.shape

        # Define o centro e os eixos da elipse
        centro_x, centro_y = int(largura / 2), int(altura / 2)
        a, b = 140, 180
        x1, y1 = centro_x - a, centro_y - b
        x2, y2 = centro_x + a, centro_y + b

        # Converte o frame para escala de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detecta faces no frame completo
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)  # Tamanho mínimo da janela de detecção
        )
        
        #if len(faces) == 0:
            #print("Nenhuma face detectada neste frame.")

        # Desenha a elipse para destacar a região de interesse (ROI)
        #cv2.ellipse(frame, (centro_x, centro_y), (a, b), 0, 0, 360, (0, 0, 255), 10)

        # Desenha elipses ao redor das faces detectadas
        for (x, y, w, h) in faces:
            if x1 < x < x2 and y1 < y < y2 and (x + w) < x2 and (y + h) < y2:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Retângulo verde

        # Codifica o frame como JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            print("Erro ao codificar o frame como JPEG.")
            return None

        return jpeg.tobytes()
    

    def sample_faces(self, frame):
        # Tenta capturar o frame atual
        ret, frame = self.get_frame()
        if not ret or frame is None:
            print("Erro: Não foi possível capturar o frame para amostragem de faces.")
            return None

        # Inverte e redimensiona o frame para padronização
        frame = cv2.flip(frame, 180)
        frame = cv2.resize(frame, (640, 480))

        # Detecta faces no frame redimensionado
        faces = self.face_cascade.detectMultiScale(
            frame,
            scaleFactor=1.1,
            minNeighbors=10,
            minSize=(50, 50),  # Tamanho mínimo da face
            maxSize=(300, 300)  # Tamanho máximo da face
        )

        # Retorna a primeira face encontrada, se existir
        for (x, y, w, h) in faces:
            cv2.rectangle(frame,(x,y), (x + w, y + h ), (0 , 255, 0),4 )
            cropped_face = frame[y:y + h, x:x + w]
            return cropped_face

        print("Nenhuma face encontrada no frame para amostragem.")
        return None

