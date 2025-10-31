import socket
import threading
import random

class HangmanServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.players = []
        self.game_state = None
        
        # 🎯 NOVO: Palavras organizadas por tema
        self.themes = {
            'animal': [
                'gato', 'cachorro', 'elefante', 'girafa', 'tigre',
                'leao', 'macaco', 'zebra', 'urso', 'panda'
            ],
            'pais': [
                'brasil', 'argentina', 'canada', 'japao', 'alemanha',
                'franca', 'italia', 'espanha', 'portugal', 'mexico'
            ],
            'computador': [
                'mouse', 'teclado', 'monitor', 'processador', 'memoria',
                'windows', 'python', 'java', 'html', 'javascript'
            ]
        }
        self.current_theme = None
        
    def select_theme_and_word(self):
        # 🎯 NOVO: Seleciona tema aleatório e palavra
        self.current_theme = random.choice(list(self.themes.keys()))
        word = random.choice(self.themes[self.current_theme])
        return word
        
    def start_game(self):
        if len(self.players) < 2:
            return
            
        # 🎯 NOVO: Seleciona tema e palavra
        word = self.select_theme_and_word()
        
        self.game_state = {
            'word': word,
            'hidden_word': ['_' for _ in word],
            'attempts_left': 6,
            'used_letters': [],
            'current_player': 0,
            'game_started': True,
            'theme': self.current_theme  # 🎯 NOVO: Adiciona tema ao estado
        }
        
        # 🎯 NOVO: Envia tema junto com outras informações
        self.broadcast(f"START:{word}:{''.join(self.game_state['hidden_word'])}:{self.game_state['attempts_left']}:{self.current_theme}")
        self.broadcast(f"TURN:{self.players[0]['username']}")
        print(f"🎮 Jogo iniciado! Tema: {self.current_theme}, Palavra: {word}")
    
    def process_guess(self, letter):
        letter = letter.lower()
        
        if letter in self.game_state['used_letters']:
            return f"ERROR:Letra {letter} já tentada"
            
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
            return "Correto!"
        else:
            self.game_state['attempts_left'] -= 1
            
            if self.game_state['attempts_left'] <= 0:
                self.broadcast(f"LOSE:{self.game_state['word']}:{self.game_state['theme']}")
                self.reset_game()
                return "DERROTA"
                
            self.broadcast(f"WRONG:{letter}:{self.game_state['attempts_left']}")
            return "Errado!"
    
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
        for client in self.clients:
            try:
                client['socket'].send(message.encode())
            except:
                self.remove_client(client)
    
    def remove_client(self, client):
        if client in self.clients:
            self.clients.remove(client)
        if client in self.players:
            self.players.remove(client)
            if client['username']:
                self.broadcast(f"LEFT:{client['username']}")
    
    def handle_client(self, client_socket, address):
        print(f"🔗 Nova conexão: {address}")
        
        username = None
        try:
            username_msg = client_socket.recv(1024).decode().strip()
            if username_msg.startswith("JOIN:"):
                username = username_msg.split(":")[1]
            else:
                client_socket.close()
                return
                
            player = {
                'socket': client_socket, 
                'username': username, 
                'address': address
            }
            self.players.append(player)
            self.clients.append(player)
            
            self.broadcast(f"JOINED:{username}")
            print(f"👤 {username} conectado. Total: {len(self.players)}")
            
            if len(self.players) >= 2 and not self.game_state:
                self.broadcast("⏳ Aguardando... Iniciando em 5s!")
                threading.Timer(5.0, self.start_game).start()
            
            while True:
                message = client_socket.recv(1024).decode().strip()
                if not message:
                    break
                    
                print(f"📨 {username}: {message}")
                
                if message.startswith("GUESS:") and self.game_state:
                    letter = message.split(":")[1]
                    current_player = self.players[self.game_state['current_player']]
                    
                    if current_player['username'] == username:
                        result = self.process_guess(letter)
                        if "VITÓRIA" not in result and "DERROTA" not in result:
                            self.next_turn()
                    
        except Exception as e:
            print(f"❌ Erro com {username}: {e}")
        finally:
            if username:
                print(f"👋 {username} desconectado")
                self.remove_client({'username': username, 'socket': client_socket})
            client_socket.close()
    
    def start_server(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"🚀 Servidor rodando em {self.host}:{self.port}")
            print("🎯 Temas disponíveis: animal, pais, computador")
            print("⏳ Aguardando conexões...")
            
            while True:
                client_socket, address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\n🛑 Servidor encerrado")
        except Exception as e:
            print(f"❌ Erro no servidor: {e}")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    server = HangmanServer()
    server.start_server()