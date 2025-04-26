import cv2
import mediapipe as mp
import numpy as np
import time

class RastreadorMovimentos:
    def __init__(self, modo=False, max_maos=2, complexidade=1, confianca_deteccao=0.5, confianca_rastreamento=0.5):
        """
        Inicializa o rastreador de movimentos.
        
        Parâmetros:
        - modo: estático (True) ou rastreamento (False)
        - max_maos: número máximo de mãos a serem rastreadas
        - complexidade: nível de complexidade do modelo (0 ou 1)
        - confianca_deteccao: limiar mínimo de confiança para detecção
        - confianca_rastreamento: limiar mínimo de confiança para rastreamento
        """
        self.modo = modo
        self.max_maos = max_maos
        self.complexidade = complexidade
        self.confianca_deteccao = confianca_deteccao
        self.confianca_rastreamento = confianca_rastreamento
        
        # Inicializar os módulos do MediaPipe
        self.mp_maos = mp.solutions.hands
        self.mp_desenho = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles
        self.maos = self.mp_maos.Hands(
            static_image_mode=self.modo,
            max_num_hands=self.max_maos,
            model_complexity=self.complexidade,
            min_detection_confidence=self.confianca_deteccao,
            min_tracking_confidence=self.confianca_rastreamento
        )
        
        # Inicializar módulo de pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=self.modo,
            model_complexity=self.complexidade,
            min_detection_confidence=self.confianca_deteccao,
            min_tracking_confidence=self.confianca_rastreamento
        )
        
        # Variáveis para calcular FPS
        self.tempo_atual = 0
        self.tempo_anterior = 0
    
    def encontrar_maos(self, imagem, desenhar=True):
        """
        Detecta mãos na imagem.
        
        Parâmetros:
        - imagem: frame da câmera
        - desenhar: se True, desenha os landmarks nas mãos
        
        Retorna:
        - imagem processada
        - lista com informações das mãos encontradas
        """
        # Converter imagem para RGB (MediaPipe requer RGB)
        imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
        self.resultados_maos = self.maos.process(imagem_rgb)
        todas_maos = []
        
        altura, largura, _ = imagem.shape
        
        if self.resultados_maos.multi_hand_landmarks:
            for id_mao, mao_landmarks in enumerate(self.resultados_maos.multi_hand_landmarks):
                info_mao = {}
                pontos_landmarks = []
                
                # Extrair coordenadas dos landmarks
                for id_lm, lm in enumerate(mao_landmarks.landmark):
                    px, py = int(lm.x * largura), int(lm.y * altura)
                    pontos_landmarks.append([id_lm, px, py])
                
                # Determinar qual mão (esquerda ou direita)
                if self.resultados_maos.multi_handedness:
                    info_mao["tipo"] = self.resultados_maos.multi_handedness[id_mao].classification[0].label
                
                info_mao["landmarks"] = pontos_landmarks
                todas_maos.append(info_mao)
                
                # Desenhar os landmarks e conexões
                if desenhar:
                    self.mp_desenho.draw_landmarks(
                        imagem, 
                        mao_landmarks,
                        self.mp_maos.HAND_CONNECTIONS,
                        self.mp_styles.get_default_hand_landmarks_style(),
                        self.mp_styles.get_default_hand_connections_style()
                    )
        
        return imagem, todas_maos
    
    def encontrar_pose(self, imagem, desenhar=True):
        """
        Detecta pose na imagem.
        
        Parâmetros:
        - imagem: frame da câmera
        - desenhar: se True, desenha os landmarks da pose
        
        Retorna:
        - imagem processada
        - lista com landmarks da pose
        """
        # Converter imagem para RGB
        imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
        self.resultados_pose = self.pose.process(imagem_rgb)
        landmarks_pose = []
        
        altura, largura, _ = imagem.shape
        
        if self.resultados_pose.pose_landmarks:
            # Extrair coordenadas dos landmarks
            for id_lm, lm in enumerate(self.resultados_pose.pose_landmarks.landmark):
                px, py = int(lm.x * largura), int(lm.y * altura)
                landmarks_pose.append([id_lm, px, py])
            
            # Desenhar os landmarks e conexões
            if desenhar:
                # Definir estilo personalizado para as conexões
                estilo_conexoes = self.mp_desenho.DrawingSpec(
                    color=(0, 255, 0),  # Cor verde
                    thickness=2,        # Espessura da linha
                    circle_radius=1     # Raio do círculo nas juntas
                )
                
                self.mp_desenho.draw_landmarks(
                    imagem,
                    self.resultados_pose.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_styles.get_default_pose_landmarks_style(),
                    connection_drawing_spec=estilo_conexoes
                )
                
        return imagem, landmarks_pose
    
    def calcular_fps(self):
        """
        Calcula os frames por segundo.
        
        Retorna:
        - valor de FPS
        """
        self.tempo_atual = time.time()
        fps = 1 / (self.tempo_atual - self.tempo_anterior)
        self.tempo_anterior = self.tempo_atual
        return int(fps)
    
    def mostrar_fps(self, imagem, fps):
        """
        Mostra o FPS na imagem.
        
        Parâmetros:
        - imagem: frame da câmera
        - fps: valor de FPS a ser mostrado
        
        Retorna:
        - imagem com FPS
        """
        cv2.putText(imagem, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return imagem
