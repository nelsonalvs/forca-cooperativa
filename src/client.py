import socket
import threading

class HangmanClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = ""
        self.connected = False
        
    def connect(self, host='localhost', port=12345):
        try:
            self.socket.connect((host, port))
            self.connected = True
            print("✅ Conectado ao servidor!")
            
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False
    
    def receive_messages(self):
        while self.connected:
            try:
                message = self.socket.recv(1024).decode()
                if not message:
                    break
                self.handle_message(message)
            except:
                break
    
    def handle_message(self, message):
        # 🎯 ATUALIZADO: Adiciona suporte a temas
        if message.startswith("START:"):
            parts = message.split(":")
            hidden = parts[2]
            attempts = parts[3]
            theme = parts[4]  # 🎯 NOVO: Recebe o tema
            print(f"\n🎮 JOGO INICIADO!")
            print(f"🎯 TEMA: {theme.upper()}")
            print(f"📏 Palavra: {hidden}")
            print(f"💡 Tentativas: {attempts}")
            
        elif message.startswith("TURN:"):
            player = message.split(":")[1]
            if player == self.username:
                print("\n🎯 SUA VEZ! Digite uma letra:")
            else:
                print(f"\n⏳ Vez de: {player}")
            
        elif message.startswith("CORRECT:"):
            parts = message.split(":")
            print(f"\n✅ Letra {parts[1]} correta! Palavra: {parts[2]}")
            
        elif message.startswith("WRONG:"):
            parts = message.split(":")
            print(f"\n❌ Letra {parts[1]} incorreta! Tentativas: {parts[2]}")
            
        elif message.startswith("WIN:"):
            parts = message.split(":")
            word = parts[1]
            theme = parts[2]  # 🎯 NOVO: Recebe tema na vitória
            print(f"\n🏆 VITÓRIA!")
            print(f"🎯 Tema: {theme}")
            print(f"📝 Palavra: {word}")
            print("🔄 Novo jogo em 5 segundos...")
            
        elif message.startswith("LOSE:"):
            parts = message.split(":")
            word = parts[1]
            theme = parts[2]  # 🎯 NOVO: Recebe tema na derrota
            print(f"\n💀 DERROTA!")
            print(f"🎯 Tema: {theme}")
            print(f"📝 A palavra era: {word}")
            print("🔄 Novo jogo em 5 segundos...")
            
        elif message.startswith("JOINED:"):
            player = message.split(":")[1]
            print(f"\n👋 {player} entrou no jogo")
            
        elif message.startswith("LEFT:"):
            player = message.split(":")[1]
            print(f"\n👋 {player} saiu")
            
        elif message.startswith("ERROR:"):
            error = message.split(":")[1]
            print(f"\n⚠️  {error}")
            
        else:
            print(f"\n📢 {message}")
    
    def send_message(self, message):
        if self.connected:
            try:
                self.socket.send(message.encode())
            except:
                self.connected = False
    
    def start_interface(self):
        print("=" * 50)
        print("🎮 JOGO DA FORCA COOPERATIVO")
        print("🎯 TEMAS: Animal, País, Computador")
        print("=" * 50)
        
        self.username = input("Digite seu nome: ")
        self.send_message(f"JOIN:{self.username}")
        
        print(f"\n👋 Olá {self.username}! Aguardando jogadores...")
        print("💡 Digite uma letra para jogar")
        print("🎯 Os temas são escolhidos automaticamente")
        print("-" * 50)
        
        while self.connected:
            try:
                user_input = input().strip().lower()
                
                if user_input == '/sair':
                    break
                elif len(user_input) == 1 and user_input.isalpha():
                    self.send_message(f"GUESS:{user_input}")
                else:
                    print("⚠️  Digite apenas UMA letra")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Erro: {e}")
        
        self.socket.close()
        print("👋 Até logo!")

if __name__ == "__main__":
    client = HangmanClient()
    if client.connect():
        client.start_interface()
    else:
        print("❌ Não foi possível conectar ao servidor")