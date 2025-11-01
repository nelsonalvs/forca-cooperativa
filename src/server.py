import socket
import threading
import random

def get_local_ip():
    """Tenta descobrir o IP local da máquina na rede."""
    try:
        # Cria um socket temporário para se conectar a um IP externo
        # Isso força o sistema a revelar qual IP local ele usaria
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)) # Conecta ao DNS do Google
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # Se falhar (ex: sem internet), retorna o IP de loopback
        return "127.0.0.1"

class HangmanServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.players = []
        self.game_state = None
        
        self.themes = {
            'animal': ['gato', 'cachorro', 'elefante', 'girafa', 'tigre', 'leao', 'macaco', 'zebra', 'urso', 'panda'],
            'pais': ['brasil', 'argentina', 'canada', 'japao', 'alemanha', 'franca', 'italia', 'espanha', 'portugal', 'mexico'],
            'computador': ['mouse', 'teclado', 'monitor', 'processador', 'memoria', 'windows', 'python', 'java', 'html', 'javascript']
        }
        self.current_theme = None
        
    def select_theme_and_word(self):
        self.current_theme = random.choice(list(self.themes.keys()))
        word = random.choice(self.themes[self.current_theme])
        return word
        
    def start_game(self):
        if len(self.players) < 2:
            return
            
        word = self.select_theme_and_word()
        self.game_state = {
            'word': word,
            'hidden_word': ['_' for _ in word],
            'attempts_left': 6,
            'used_letters': [],
            'current_player': 0,
            'game_started': True,
            'theme': self.current_theme
        }
        
        self.broadcast(f"START:{word}:{''.join(self.game_state['hidden_word'])}:{self.game_state['attempts_left']}:{self.current_theme}")
        self.broadcast(f"TURN:{self.players[0]['username']}")
        print(f"🎮 Jogo iniciado! Tema: {self.current_theme}, Palavra: {word}")
    
    def process_guess(self, letter):
        letter = letter.lower()
        
        if letter in self.game_state['used_letters']:
            # Envia o erro apenas para o jogador atual
            current_player_socket = self.players[self.game_state['current_player']]['socket']
            try:
                current_player_socket.send(f"ERROR:Letra {letter} já tentada".encode())
            except Exception as e:
                print(f"Erro ao enviar msg de erro: {e}")
            return f"Letra {letter} já tentada" # Retorno interno, não afeta o turno
            
        self.game_state['used_letters'].append(letter)
        word = self.game_state['word']
        
        if letter in word:
            for i, char in enumerate(word):
                if char == letter:
                    self.game_state['hidden_word'][i] = letter
            
            if ''.join(self.game_state['hidden_word']) == word:
                self.broadcast(f"WIN:{self.game_state['word']}:{self.game_state['theme']}")
                self.reset_game()
                return "VITÓRIA"
                
            self.broadcast(f"CORRECT:{letter}:{''.join(self.game_state['hidden_word'])}")
            return "Correto!" # Retorno interno
        else:
            self.game_state['attempts_left'] -= 1
            
            if self.game_state['attempts_left'] <= 0:
                self.broadcast(f"LOSE:{self.game_state['word']}:{self.game_state['theme']}")
                self.reset_game()
                return "DERROTA"
                
            self.broadcast(f"WRONG:{letter}:{self.game_state['attempts_left']}")
            return "Errado!" # Retorno interno
    
    def next_turn(self):
        self.game_state['current_player'] = (self.game_state['current_player'] + 1) % len(self.players)
        next_player = self.players[self.game_state['current_player']]['username']
        self.broadcast(f"TURN:{next_player}")
    
    def reset_game(self):
        self.game_state = None
        self.current_theme = None
        print("🔄 Reiniciando jogo em 5 segundos...")
        threading.Timer(5.0, self.start_game).start()
    
    def broadcast(self, message):
        # Transmite para todos os clientes na lista
        for client in list(self.clients): # Usamos list() para criar uma cópia
            try:
                client['socket'].send(message.encode())
            except:
                # Se falhar, remove o cliente
                self.remove_client(client)
    
    def remove_client(self, client):
        if client in self.clients:
            self.clients.remove(client)
        
        player_to_remove = None
        for p in self.players:
            if p['socket'] == client['socket']:
                player_to_remove = p
                break
        
        if player_to_remove:
            self.players.remove(player_to_remove)
            if player_to_remove['username']:
                print(f"👋 {player_to_remove['username']} desconectado")
                self.broadcast(f"LEFT:{player_to_remove['username']}")
        
        # Lógica para parar o jogo se um jogador sair (opcional, mas recomendado)
        if self.game_state and len(self.players) < 2:
            print("❌ Jogador saiu. Pausando o jogo.")
            self.broadcast("INFO:Um jogador saiu. O jogo está pausado até outro entrar.")
            self.game_state = None # Reseta o jogo
            
    def handle_client(self, client_socket, address):
        print(f"🔗 Nova conexão recebida de: {address}")
        
        username = None
        player_info = None
        try:
            # Espera a mensagem JOIN
            username_msg = client_socket.recv(1024).decode().strip()
            if username_msg.startswith("JOIN:"):
                username = username_msg.split(":", 1)[1] # split 1 vez
            else:
                print("Conexão sem JOIN. Fechando.")
                client_socket.close()
                return
                
            player_info = {'socket': client_socket, 'username': username, 'address': address}
            self.players.append(player_info)
            self.clients.append(player_info) # Adiciona a lista geral de clientes
            
            self.broadcast(f"JOINED:{username}")
            print(f"👤 {username} conectado. Total de jogadores: {len(self.players)}")
            
            # Se já houver um jogo, mas só 1 jogador, e outro entrar, inicia.
            if len(self.players) >= 2 and not self.game_state:
                self.broadcast("⏳ Jogadores suficientes! Iniciando em 5s!")
                threading.Timer(5.0, self.start_game).start()
            
            while True:
                message = client_socket.recv(1024).decode().strip()
                if not message:
                    break # Cliente desconectou
                    
                print(f"📨 {username}: {message}")
                
                if message.startswith("GUESS:") and self.game_state:
                    letter = message.split(":", 1)[1]
                    current_player = self.players[self.game_state['current_player']]
                    
                    if current_player['username'] == username:
                        result = self.process_guess(letter)
                        # Só passa o turno se o jogo NÃO acabou e a letra não foi repetida
                        if "VITÓRIA" not in result and "DERROTA" not in result and "já tentada" not in result:
                            self.next_turn()
                    else:
                        # Envia erro se não for a vez do jogador
                        try:
                            client_socket.send("ERROR:Não é a sua vez!".encode())
                        except:
                            pass # A desconexão será tratada no loop principal
                
        except Exception as e:
            print(f"❌ Erro com {username} ({address}): {e}")
        finally:
            # Garante que o cliente seja removido
            if player_info:
                self.remove_client(player_info)
            client_socket.close()
    
    def start_server(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            server_ip = get_local_ip() # Chama a nova função
            
            print("="*50)
            print(f"🚀 Servidor da Forca rodando!")
            print(f"📡 Escutando em todas as interfaces ({self.host}:{self.port})")
            print("="*50)
            print(f"💡 Para outros computadores na mesma rede,")
            print(f"   conecte-se ao IP: {server_ip}:{self.port}")
            print("="*50)
            
            while True:
                client_socket, address = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
                client_thread.daemon = True # Permite que o programa feche mesmo com threads ativas
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\n🛑 Servidor encerrado pelo usuário.")
        except Exception as e:
            print(f"❌ Erro fatal no servidor: {e}")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    server = HangmanServer()
    server.start_server()