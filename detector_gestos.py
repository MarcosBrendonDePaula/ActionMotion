import os
import json
import numpy as np
import cv2
from executor_acoes import ExecutorAcoes

class DetectorGestos:
    def __init__(self, diretorio_gestos="gestos"):
        """
        Inicializa o detector de gestos.
        
        Parâmetros:
        - diretorio_gestos: diretório onde os gestos serão salvos
        """
        self.diretorio_gestos = diretorio_gestos
        self.arquivo_gestos = os.path.join(diretorio_gestos, "gestos.json")
        self.gestos = {}
        
        # Inicializar executor de ações
        self.executor = ExecutorAcoes()
        
        # Registro de ações em execução
        self.acoes_em_execucao = {}
        
        # Tempo mínimo entre execuções da mesma ação (em segundos)
        self.tempo_minimo_entre_acoes = 1.0
        self.ultima_execucao = {}
        
        # Criar diretório se não existir
        if not os.path.exists(diretorio_gestos):
            os.makedirs(diretorio_gestos)
            
        # Carregar gestos salvos se existirem
        if os.path.exists(self.arquivo_gestos):
            try:
                with open(self.arquivo_gestos, 'r', encoding='utf-8') as f:
                    self.gestos = json.load(f)
                print(f"Carregados {len(self.gestos)} gestos do arquivo.")
            except Exception as e:
                print(f"Erro ao carregar gestos: {e}")
                self.gestos = {}
    
    def capturar_gesto(self, maos, pose):
        """
        Captura o estado atual das mãos e pose para criar um novo gesto.
        
        Parâmetros:
        - maos: lista com informações das mãos detectadas
        - pose: lista com landmarks da pose
        
        Retorna:
        - dicionário com o estado capturado
        """
        captura = {
            "maos": [],
            "pose": []
        }
        
        # Capturar estado das mãos
        for mao in maos:
            captura["maos"].append({
                "tipo": mao.get("tipo", "Desconhecido"),
                "landmarks": mao["landmarks"]
            })
        
        # Capturar pose
        if pose:
            captura["pose"] = pose
            
        return captura
    
    def salvar_gesto(self, nome, descricao, captura, acao=None):
        """
        Salva um novo gesto no arquivo.
        
        Parâmetros:
        - nome: nome do gesto
        - descricao: descrição do gesto
        - captura: dados capturados do gesto
        - acao: dicionário com informações da ação a ser executada (opcional)
        
        Retorna:
        - True se salvou com sucesso, False caso contrário
        """
        try:
            # Adicionar o novo gesto ao dicionário
            self.gestos[nome] = {
                "descricao": descricao,
                "captura": captura,
                "acao": acao
            }
            
            # Salvar no arquivo
            with open(self.arquivo_gestos, 'w', encoding='utf-8') as f:
                json.dump(self.gestos, f, indent=2, ensure_ascii=False)
            
            print(f"Gesto '{nome}' salvo com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao salvar gesto: {e}")
            return False
    
    def remover_gesto(self, nome):
        """
        Remove um gesto do arquivo.
        
        Parâmetros:
        - nome: nome do gesto a ser removido
        
        Retorna:
        - True se removeu com sucesso, False caso contrário
        """
        if nome in self.gestos:
            try:
                del self.gestos[nome]
                
                # Atualizar arquivo
                with open(self.arquivo_gestos, 'w', encoding='utf-8') as f:
                    json.dump(self.gestos, f, indent=2, ensure_ascii=False)
                
                print(f"Gesto '{nome}' removido com sucesso!")
                return True
            except Exception as e:
                print(f"Erro ao remover gesto: {e}")
                return False
        else:
            print(f"Gesto '{nome}' não encontrado.")
            return False
    
    def associar_acao(self, nome_gesto, tipo_acao, parametros):
        """
        Associa uma ação a um gesto já cadastrado.
        
        Parâmetros:
        - nome_gesto: nome do gesto
        - tipo_acao: tipo da ação (teclado, mouse, personalizada)
        - parametros: parâmetros da ação
        
        Retorna:
        - True se associou com sucesso, False caso contrário
        """
        if nome_gesto not in self.gestos:
            print(f"Gesto '{nome_gesto}' não encontrado.")
            return False
            
        try:
            # Criar objeto de ação
            acao = {
                "tipo": tipo_acao,
                "parametros": parametros
            }
            
            # Associar ao gesto
            self.gestos[nome_gesto]["acao"] = acao
            
            # Salvar no arquivo
            with open(self.arquivo_gestos, 'w', encoding='utf-8') as f:
                json.dump(self.gestos, f, indent=2, ensure_ascii=False)
            
            print(f"Ação associada ao gesto '{nome_gesto}' com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao associar ação: {e}")
            return False
    
    def remover_acao(self, nome_gesto):
        """
        Remove a ação associada a um gesto.
        
        Parâmetros:
        - nome_gesto: nome do gesto
        
        Retorna:
        - True se removeu com sucesso, False caso contrário
        """
        if nome_gesto not in self.gestos:
            print(f"Gesto '{nome_gesto}' não encontrado.")
            return False
            
        if "acao" not in self.gestos[nome_gesto]:
            print(f"Gesto '{nome_gesto}' não possui ação associada.")
            return False
            
        try:
            # Remover ação
            del self.gestos[nome_gesto]["acao"]
            
            # Salvar no arquivo
            with open(self.arquivo_gestos, 'w', encoding='utf-8') as f:
                json.dump(self.gestos, f, indent=2, ensure_ascii=False)
            
            print(f"Ação removida do gesto '{nome_gesto}' com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao remover ação: {e}")
            return False
    
    def calcular_similaridade(self, landmarks1, landmarks2, tipo="mao"):
        """
        Calcula a similaridade entre dois conjuntos de landmarks.
        
        Parâmetros:
        - landmarks1: primeiro conjunto de landmarks
        - landmarks2: segundo conjunto de landmarks
        - tipo: tipo de landmarks ('mao' ou 'pose')
        
        Retorna:
        - valor de similaridade (0 a 1, onde 1 é identico)
        """
        if not landmarks1 or not landmarks2:
            return 0
        
        # Extrair coordenadas
        pontos1 = np.array([[lm[1], lm[2]] for lm in landmarks1])
        pontos2 = np.array([[lm[1], lm[2]] for lm in landmarks2])
        
        # Verificar se têm o mesmo número de pontos
        if len(pontos1) != len(pontos2):
            # Se o número de pontos for diferente, pode ser que uma mão tenha mais landmarks detectados que outra
            # Vamos usar os landmarks em comum
            min_pontos = min(len(pontos1), len(pontos2))
            pontos1 = pontos1[:min_pontos]
            pontos2 = pontos2[:min_pontos]
        
        # Normalizar para remover efeitos de escala e posição
        pontos1 = self._normalizar_pontos(pontos1)
        pontos2 = self._normalizar_pontos(pontos2)
        
        # Calcular distância média entre os pontos correspondentes
        distancias = np.sqrt(np.sum((pontos1 - pontos2) ** 2, axis=1))
        distancia_media = np.mean(distancias)
        
        # Converter distância em similaridade (1 - distância normalizada)
        # Quanto menor a distância, maior a similaridade
        similaridade = max(0, 1 - (distancia_media / 2.0))
        
        return similaridade
    
    def _normalizar_pontos(self, pontos):
        """
        Normaliza um conjunto de pontos para remover efeitos de escala e posição.
        
        Parâmetros:
        - pontos: array numpy com coordenadas (x, y)
        
        Retorna:
        - pontos normalizados
        """
        # Remover translação: subtrair o centróide
        centro = np.mean(pontos, axis=0)
        pontos_centralizados = pontos - centro
        
        # Remover efeito de escala: dividir pela distância média ao centro
        distancias = np.sqrt(np.sum(pontos_centralizados ** 2, axis=1))
        distancia_media = np.mean(distancias)
        
        # Evitar divisão por zero
        if distancia_media < 0.0001:
            return pontos_centralizados
        
        return pontos_centralizados / distancia_media
    
    def detectar_gestos(self, maos, pose, limiar_similaridade=0.85):
        """
        Detecta quais gestos estão sendo realizados com base nos landmarks atuais.
        
        Parâmetros:
        - maos: lista com informações das mãos detectadas
        - pose: lista com landmarks da pose
        - limiar_similaridade: valor mínimo de similaridade para considerar um gesto detectado
        
        Retorna:
        - dicionário com os gestos detectados e suas similaridades
        """
        gestos_detectados = {}
        
        # Se não temos gestos cadastrados ou não detectamos mãos/pose, retorna vazio
        if not self.gestos or (not maos and not pose):
            return gestos_detectados
        
        # Para cada gesto cadastrado
        for nome_gesto, info_gesto in self.gestos.items():
            captura = info_gesto["captura"]
            melhor_similaridade = 0
            
            # Verificar similaridade das mãos
            if maos and captura["maos"]:
                for mao_atual in maos:
                    for mao_capturada in captura["maos"]:
                        # Verificar se são do mesmo tipo (esquerda/direita)
                        if mao_atual.get("tipo", "") == mao_capturada.get("tipo", ""):
                            similaridade = self.calcular_similaridade(
                                mao_atual["landmarks"], 
                                mao_capturada["landmarks"],
                                "mao"
                            )
                            melhor_similaridade = max(melhor_similaridade, similaridade)
            
            # Verificar similaridade da pose
            if pose and captura["pose"]:
                similaridade_pose = self.calcular_similaridade(
                    pose, 
                    captura["pose"],
                    "pose"
                )
                melhor_similaridade = max(melhor_similaridade, similaridade_pose)
            
            # Se a similaridade estiver acima do limiar, considerar o gesto detectado
            if melhor_similaridade >= limiar_similaridade:
                gestos_detectados[nome_gesto] = {
                    "descricao": info_gesto["descricao"],
                    "similaridade": melhor_similaridade,
                    "acao": info_gesto.get("acao", None)
                }
                
                # Executar ação associada, se existir
                self._executar_acao_do_gesto(nome_gesto, info_gesto.get("acao", None))
        
        return gestos_detectados
    
    def _executar_acao_do_gesto(self, nome_gesto, acao):
        """
        Executa a ação associada a um gesto detectado.
        
        Parâmetros:
        - nome_gesto: nome do gesto detectado
        - acao: informações da ação a ser executada
        """
        import time
        
        # Se não tem ação, não fazer nada
        if not acao:
            return
            
        # Verificar tempo mínimo entre execuções
        tempo_atual = time.time()
        if nome_gesto in self.ultima_execucao:
            tempo_desde_ultima = tempo_atual - self.ultima_execucao[nome_gesto]
            if tempo_desde_ultima < self.tempo_minimo_entre_acoes:
                # Muito cedo para executar novamente
                return
        
        # Executar a ação
        tipo_acao = acao.get("tipo", "")
        parametros = acao.get("parametros", {})
        
        if tipo_acao:
            sucesso = self.executor.executar_acao(tipo_acao, parametros)
            if sucesso:
                # Registrar momento da execução
                self.ultima_execucao[nome_gesto] = tempo_atual
                print(f"Executada ação do gesto '{nome_gesto}'")
    
    def listar_acoes_disponiveis(self):
        """
        Lista todas as ações disponíveis para associação.
        
        Retorna:
        - dicionário com as ações disponíveis
        """
        return self.executor.listar_acoes_disponiveis()
    
    def listar_gestos(self):
        """
        Lista todos os gestos cadastrados.
        
        Retorna:
        - lista de tuplas (nome, descrição)
        """
        return [(nome, info["descricao"]) for nome, info in self.gestos.items()]