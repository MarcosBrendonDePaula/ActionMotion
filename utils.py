import cv2
import os

def listar_cameras():
    """
    Lista todas as câmeras disponíveis no sistema.
    
    Retorna:
    - dicionário com índices e status das câmeras
    """
    cameras_disponiveis = {}
    for i in range(10):  # Verifica até 10 câmeras
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cameras_disponiveis[i] = "Disponível"
            else:
                cameras_disponiveis[i] = "Indisponível (Não recebe frames)"
            cap.release()
    
    if not cameras_disponiveis:
        print("Nenhuma câmera encontrada.")
    
    return cameras_disponiveis

def selecionar_camera():
    """
    Permite ao usuário selecionar uma câmera.
    
    Retorna:
    - índice da câmera selecionada
    """
    cameras = listar_cameras()
    
    if not cameras:
        print("Usando câmera padrão (0).")
        return 0
    
    print("\n=== Câmeras Disponíveis ===")
    for idx, status in cameras.items():
        print(f"Câmera {idx}: {status}")
    
    try:
        escolha = int(input("\nSelecione o número da câmera: "))
        if escolha in cameras:
            print(f"Câmera {escolha} selecionada.")
            return escolha
        else:
            print("Câmera inválida. Usando câmera padrão (0).")
            return 0
    except ValueError:
        print("Entrada inválida. Usando câmera padrão (0).")
        return 0

def criar_diretorios():
    """
    Cria os diretórios necessários para o projeto.
    """
    # Diretório para armazenar os gestos
    if not os.path.exists("gestos"):
        os.makedirs("gestos")
        print("Diretório de gestos criado.")
    
    return True

def mostrar_ajuda_tela(imagem):
    """
    Adiciona informações de ajuda à imagem.
    
    Parâmetros:
    - imagem: frame da câmera
    
    Retorna:
    - imagem com informações de ajuda
    """
    altura, largura, _ = imagem.shape
    
    # Informações no topo da tela
    cv2.putText(imagem, "RASTREADOR DE MOVIMENTOS", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Comandos na parte inferior da tela
    y = altura - 20
    cv2.putText(imagem, "q: Sair", (10, y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    y -= 25
    cv2.putText(imagem, "c: Trocar câmera", (10, y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    y -= 25
    cv2.putText(imagem, "r: Capturar gesto", (10, y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    y -= 25
    cv2.putText(imagem, "a: Editar ações", (10, y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    y -= 25
    cv2.putText(imagem, "l: Listar gestos", (10, y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    y -= 25
    cv2.putText(imagem, "d: Remover gesto", (10, y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    y -= 25
    cv2.putText(imagem, "s: Mostrar/ocultar ações", (10, y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    return imagem