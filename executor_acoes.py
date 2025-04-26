import time
import threading
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController

class ExecutorAcoes:
    def __init__(self):
        """
        Inicializa o executor de ações.
        """
        self.teclado = KeyboardController()
        self.mouse = MouseController()
        self.acoes_predefinidas = {
            # Ações do teclado
            "tecla_enter": self._tecla_enter,
            "tecla_space": self._tecla_espaco,
            "tecla_esc": self._tecla_esc,
            "tecla_ctrl_c": self._tecla_ctrl_c,
            "tecla_ctrl_v": self._tecla_ctrl_v,
            "tecla_alt_tab": self._tecla_alt_tab,
            
            # Controles de slides
            "slide_avancar": self._slide_avancar,
            "slide_retroceder": self._slide_retroceder,
            "slide_inicio": self._slide_inicio,
            "slide_fim": self._slide_fim,
            
            # Ações do mouse
            "clique_esquerdo": self._clique_esquerdo,
            "clique_direito": self._clique_direito,
            "clique_duplo": self._clique_duplo,
            "scroll_cima": self._scroll_cima,
            "scroll_baixo": self._scroll_baixo,
        }
        
        # Registro de ações personalizadas
        self.acoes_personalizadas = {}
        
        # Flag para controlar execução contínua
        self.executando_continuo = False
    
    # === Ações de teclado ===
    def _tecla_enter(self):
        self.teclado.press(Key.enter)
        self.teclado.release(Key.enter)
    
    def _tecla_espaco(self):
        self.teclado.press(Key.space)
        self.teclado.release(Key.space)
    
    def _tecla_esc(self):
        self.teclado.press(Key.esc)
        self.teclado.release(Key.esc)
    
    def _tecla_ctrl_c(self):
        self.teclado.press(Key.ctrl)
        self.teclado.press('c')
        self.teclado.release('c')
        self.teclado.release(Key.ctrl)
    
    def _tecla_ctrl_v(self):
        self.teclado.press(Key.ctrl)
        self.teclado.press('v')
        self.teclado.release('v')
        self.teclado.release(Key.ctrl)
    
    def _tecla_alt_tab(self):
        self.teclado.press(Key.alt)
        self.teclado.press(Key.tab)
        self.teclado.release(Key.tab)
        self.teclado.release(Key.alt)
    
    # === Controles de apresentação de slides ===
    def _slide_avancar(self):
        """
        Avança para o próximo slide (seta direita, Page Down, espaço, ou N)
        """
        # Podemos usar diferentes teclas que funcionam em vários programas
        # Opção 1: Seta direita
        self.teclado.press(Key.right)
        self.teclado.release(Key.right)
    
    def _slide_retroceder(self):
        """
        Volta para o slide anterior (seta esquerda, Page Up, ou P)
        """
        # Opção 1: Seta esquerda
        self.teclado.press(Key.left)
        self.teclado.release(Key.left)
    
    def _slide_inicio(self):
        """
        Vai para o primeiro slide (Home)
        """
        self.teclado.press(Key.home)
        self.teclado.release(Key.home)
    
    def _slide_fim(self):
        """
        Vai para o último slide (End)
        """
        self.teclado.press(Key.end)
        self.teclado.release(Key.end)
    
    # === Ações de mouse ===
    def _clique_esquerdo(self):
        self.mouse.click(Button.left)
    
    def _clique_direito(self):
        self.mouse.click(Button.right)
    
    def _clique_duplo(self):
        self.mouse.click(Button.left, 2)
    
    def _scroll_cima(self):
        self.mouse.scroll(0, 2)
    
    def _scroll_baixo(self):
        self.mouse.scroll(0, -2)
    
    def digitar_texto(self, texto):
        """
        Digita um texto caractere por caractere.
        
        Parâmetros:
        - texto: texto a ser digitado
        """
        for caractere in texto:
            self.teclado.press(caractere)
            self.teclado.release(caractere)
            time.sleep(0.01)  # Pequeno delay para simular digitação real
    
    def mover_mouse(self, x, y, absoluto=False):
        """
        Move o cursor do mouse para uma posição.
        
        Parâmetros:
        - x, y: coordenadas de destino
        - absoluto: se True, move para posição absoluta na tela;
                    se False, move relativamente à posição atual
        """
        if absoluto:
            self.mouse.position = (x, y)
        else:
            current_x, current_y = self.mouse.position
            self.mouse.position = (current_x + x, current_y + y)
    
    def registrar_acao_personalizada(self, nome, funcao):
        """
        Registra uma ação personalizada.
        
        Parâmetros:
        - nome: nome da ação
        - funcao: função a ser executada
        """
        self.acoes_personalizadas[nome] = funcao
    
    def executar_acao(self, tipo_acao, parametros=None):
        """
        Executa uma ação com base no tipo e parâmetros.
        
        Parâmetros:
        - tipo_acao: string identificando o tipo de ação
        - parametros: parâmetros adicionais da ação
        
        Retorna:
        - True se a ação foi executada com sucesso, False caso contrário
        """
        # Se não tiver parâmetros, inicializar como dicionário vazio
        if parametros is None:
            parametros = {}
        
        try:
            # Verificar tipo de ação
            if tipo_acao == "teclado":
                # Ação de teclado
                tecla = parametros.get("tecla", "")
                if tecla:
                    if tecla in self.acoes_predefinidas:
                        # Ação predefinida
                        self.acoes_predefinidas[tecla]()
                    elif len(tecla) == 1:
                        # Tecla única
                        self.teclado.press(tecla)
                        self.teclado.release(tecla)
                    else:
                        # Sequência de teclas
                        for t in tecla:
                            self.teclado.press(t)
                            self.teclado.release(t)
                            time.sleep(0.05)
                
                # Se tem texto para digitar
                texto = parametros.get("texto", "")
                if texto:
                    self.digitar_texto(texto)
                
            elif tipo_acao == "slide":
                # Ação de controle de slides
                acao = parametros.get("acao", "")
                comando = f"slide_{acao}" if acao else ""
                if comando in self.acoes_predefinidas:
                    self.acoes_predefinidas[comando]()
                else:
                    # Tecla personalizada para controle de slides
                    tecla = parametros.get("tecla", "")
                    if tecla:
                        if hasattr(Key, tecla.lower()):
                            # Se for uma tecla especial (como Page_down)
                            key_obj = getattr(Key, tecla.lower())
                            self.teclado.press(key_obj)
                            self.teclado.release(key_obj)
                        else:
                            # Se for uma tecla comum (como 'n' ou 'p')
                            self.teclado.press(tecla)
                            self.teclado.release(tecla)
            
            elif tipo_acao == "mouse":
                # Ação de mouse
                acao = parametros.get("acao", "")
                if acao in self.acoes_predefinidas:
                    self.acoes_predefinidas[acao]()
                
                # Se tem posição para mover
                if "x" in parametros and "y" in parametros:
                    absoluto = parametros.get("absoluto", False)
                    self.mover_mouse(parametros["x"], parametros["y"], absoluto)
            
            elif tipo_acao == "personalizada":
                # Ação personalizada
                nome_acao = parametros.get("nome", "")
                if nome_acao in self.acoes_personalizadas:
                    self.acoes_personalizadas[nome_acao]()
            
            else:
                print(f"Tipo de ação desconhecido: {tipo_acao}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Erro ao executar ação {tipo_acao}: {e}")
            return False
    
    def iniciar_execucao_continua(self, tipo_acao, parametros=None, intervalo=1.0):
        """
        Inicia execução contínua de uma ação em loop.
        
        Parâmetros:
        - tipo_acao: string identificando o tipo de ação
        - parametros: parâmetros adicionais da ação
        - intervalo: tempo em segundos entre execuções
        """
        # Parar execução anterior se existir
        self.parar_execucao_continua()
        
        # Iniciar nova execução
        self.executando_continuo = True
        
        # Criar thread para execução contínua
        def execucao_loop():
            while self.executando_continuo:
                self.executar_acao(tipo_acao, parametros)
                time.sleep(intervalo)
        
        # Iniciar thread
        thread = threading.Thread(target=execucao_loop)
        thread.daemon = True
        thread.start()
    
    def parar_execucao_continua(self):
        """
        Para a execução contínua de ações.
        """
        self.executando_continuo = False
    
    def listar_acoes_disponiveis(self):
        """
        Lista todas as ações predefinidas disponíveis.
        
        Retorna:
        - dicionário com grupos de ações
        """
        acoes = {
            "teclado": [
                {"id": "tecla_enter", "nome": "Tecla Enter"},
                {"id": "tecla_space", "nome": "Tecla Espaço"},
                {"id": "tecla_esc", "nome": "Tecla ESC"},
                {"id": "tecla_ctrl_c", "nome": "Ctrl+C (Copiar)"},
                {"id": "tecla_ctrl_v", "nome": "Ctrl+V (Colar)"},
                {"id": "tecla_alt_tab", "nome": "Alt+Tab (Alternar janelas)"}
            ],
            "slides": [
                {"id": "slide_avancar", "nome": "Avançar Slide (Seta Direita)"},
                {"id": "slide_retroceder", "nome": "Retroceder Slide (Seta Esquerda)"},
                {"id": "slide_inicio", "nome": "Primeiro Slide (Home)"},
                {"id": "slide_fim", "nome": "Último Slide (End)"}
            ],
            "mouse": [
                {"id": "clique_esquerdo", "nome": "Clique Esquerdo"},
                {"id": "clique_direito", "nome": "Clique Direito"},
                {"id": "clique_duplo", "nome": "Clique Duplo"},
                {"id": "scroll_cima", "nome": "Scroll para Cima"},
                {"id": "scroll_baixo", "nome": "Scroll para Baixo"}
            ]
        }
        
        # Adicionar ações personalizadas
        if self.acoes_personalizadas:
            acoes["personalizadas"] = [
                {"id": nome, "nome": nome} for nome in self.acoes_personalizadas.keys()
            ]
        
        return acoes