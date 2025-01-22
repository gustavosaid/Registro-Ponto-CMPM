import cv2 

class VideoCamera(object):
    def __init__(self):
        # Abre a câmera
        self.face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        self.video = cv2.VideoCapture(0) #abre a camera do pc 
        
        if not self.video.isOpened():
            print("Erro ao abrir a câmera.")  # Verifica se a câmera foi aberta corretamente

    def __del__(self):
        # Libera a câmera ao destruir a classe
        self.video.release()

    def restart(self):
        # Reinicia a câmera
        self.video.release()
        self.video = cv2.VideoCapture(0)

    #retorna o frame modo normal do objeto
    def get_camera(self):
        # Lê o frame da câmera
        ret, frame = self.video.read()
        if not ret:
            print("Falha ao capturar o frame.")  # Verifica se a captura do frame foi bem-sucedida
            return None
        
        # Converte o frame em imagem JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            print("Erro ao codificar o frame para JPEG.")  # Verifica se a codificação foi bem-sucedida
            return None
        
        return ret, frame
    
    def detect_face(self):
        ret, frame = self.video.read() #leitura frame
        if not ret: #verifica se a captura do frame foi bem sucedida
            print("Falha ao capturar o frame")
            return None
        
        #conventendo para escala de cinza para melhorar a detecção de faces
        gray = cv2.cvtColor(frame,cv2.COLOR_BGRGRAY)
        
        #detecta faces do frame
        faces = self.face_cascade.detectMultoScale(gray,1.3,5)
        
        #desenho de um retangulo em torno das faces detectadas
        for (x, y, w, h) in faces_detected:
            cv2.rectangle(frame, (x, y), (x+w, y+h),(255,0,0),2 )
        
        #retorn o frame com a imagem detectada
        ret,jpeg = cv2.imencode('.jpg',frame)
        return jpeg,tobytes() #converte o frame para formato jpeg
