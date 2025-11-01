import socket
import threading

class HangmanClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = ""
        self.connected = False
        
    def connect(self, host='localhost', port=5000):
        try:
            print(f"🔗 Conectando ao servidor {host}:{port}...")
            self.socket.connect((host, port))
            self.connected = True
            print("✅ Conectado ao servidor!")
            
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
        except socket.error as e:
            # Erros comuns:
            if e.errno == 10061: # Connection refused
                print(f"❌ Erro ao conectar: Conexão recusada.")
                print("   Verifique se o IP está correto e se o servidor está rodando.")
            elif e.errno == 10060: # Connection timed out
                print(f"❌ Erro ao conectar: Tempo esgotado.")
                print("   Verifique o IP e se o Firewall está bloqueando a porta 5000.")
            else:
                print(f"❌ Erro de socket ao conectar: {e}")
            return False
        except Exception as e:
            print(f"❌ Erro desconhecido ao conectar: {e}")
            return False
    
    def receive_messages(self):
        while self.connected:
            try:
                message = self.socket.recv(1024).decode()
                if not message:
                    print("\n🔌 Conexão perdida com o servidor.")
                    self.connected = False
                    break
                
                # Trata múltiplas mensagens de uma vez (caso cheguem juntas)
                messages = message.split('\n') # Simples split, pode falhar se a msg tiver \n
                for msg in messages:
                    if msg: # Ignora strings vazias
                        self.handle_message(msg)
            except:
                print("\n🔌 Erro ao receber dados. Desconectando.")
                self.connected = False
                break
    
    def handle_message(self, message):
        # Usamos .strip() para limpar espaços em branco
        message = message.strip()
        
        try:
            if message.startswith("START:"):
                parts = message.split(":")
                # parts[0] = START
                # parts[1] = word (não usamos no cliente, só para debug)
                hidden = parts[2]
                attempts = parts[3]
                theme = parts[4]
                print(f"\n" + "="*30)
                print(f"🎮 JOGO INICIADO!")
                print(f"🎯 TEMA: {theme.upper()}")
                print(f"📏 Palavra: {hidden}")
                print(f"💡 Tentativas: {attempts}")
                print("="*30)
                
            elif message.startswith("TURN:"):
                player = message.split(":", 1)[1]
                if player == self.username:
                    print(f"\n" + "-"*30)
                    print(f"🎯 SUA VEZ! ({player})")
                    print(f"Digite uma letra:")
                    print(f"-"*30)
                else:
                    print(f"\n⏳ Vez de: {player}")
                
            elif message.startswith("CORRECT:"):
                parts = message.split(":")
                print(f"✅ Letra '{parts[1]}' correta! Palavra: {parts[2]}")
                
            elif message.startswith("WRONG:"):
                parts = message.split(":")
                print(f"❌ Letra '{parts[1]}' incorreta! Tentativas restantes: {parts[2]}")
                
            elif message.startswith("WIN:"):
                parts = message.split(":")
                word = parts[1]
                theme = parts[2]
                print(f"\n" + "🏆"*10)
                print(f"   VITÓRIA!")
                print(f"   Tema: {theme}")
                print(f"   Palavra: {word}")
                print("🏆"*10)
                print("🔄 Novo jogo em 5 segundos...")
                
            elif message.startswith("LOSE:"):
                parts = message.split(":")
                word = parts[1]
                theme = parts[2]
                print(f"\n" + "💀"*10)
                print(f"   DERROTA!")
                print(f"   Tema: {theme}")
                print(f"   A palavra era: {word}")
                print("💀"*10)
                print("🔄 Novo jogo em 5 segundos...")
                
            elif message.startswith("JOINED:"):
                player = message.split(":", 1)[1]
                print(f"\n👋 {player} entrou no jogo")
                
            elif message.startswith("LEFT:"):
                player = message.split(":", 1)[1]
                print(f"\n👋 {player} saiu do jogo")
                
            elif message.startswith("ERROR:"):
                error = message.split(":", 1)[1]
                print(f"\n⚠️ ERRO: {error}")
                # Se o erro for de letra repetida, pede para jogar de novo
                if "sua vez" in error or "já tentada" in error:
                     print(f"Digite uma letra:")

            else:
                # Mensagens genéricas do servidor (ex: "Aguardando...")
                print(f"\n📢 [SERVIDOR] {message}")
        
        except Exception as e:
            print(f"[DEBUG] Erro ao processar mensagem: '{message}' -> {e}")

    
    def send_message(self, message):
        if self.connected:
            try:
                self.socket.send(message.encode())
            except:
                print("❌ Erro ao enviar mensagem. Conexão pode ter caído.")
                self.connected = False
    
    def start_interface(self):
        # Loop de input do usuário
        while self.connected:
            try:
                user_input = input().strip().lower()
                
                if not self.connected: # Verifica de novo caso a thread tenha desconectado
                    break
                    
                if user_input == '/sair':
                    print("Saindo...")
                    break
                elif len(user_input) == 1 and user_input.isalpha():
                    self.send_message(f"GUESS:{user_input}")
                elif user_input: # Ignora 'Enter' vazio
                    print("⚠️ Digite apenas UMA letra (ou '/sair' para sair)")
                    
            except KeyboardInterrupt:
                print("\nSaindo...")
                break
            except Exception as e:
                print(f"Erro no loop de input: {e}")
                break
        
        self.connected = False
        self.socket.close()
        print("👋 Até logo!")

if __name__ == "__main__":
    print("=" * 50)
    print("🎮 JOGO DA FORCA EM REDE")
    print("=" * 50)
    
    # --- MUDANÇA PRINCIPAL AQUI ---
    server_ip = input("Digite o IP do servidor (ou pressione ENTER para 'localhost'): ")
    if not server_ip:
        server_ip = 'localhost'
        print(f"Conectando em 'localhost'...")
    # --- FIM DA MUDANÇA ---

    client = HangmanClient()
    
    # Tenta conectar com o IP fornecido
    if client.connect(host=server_ip, port=5000):
        # Só pede o nome DEPOIS de conectar
        username = ""
        while not username:
             username = input("Digite seu nome: ").strip()
             
        client.username = username
        client.send_message(f"JOIN:{client.username}")
        
        print(f"\n👋 Olá {client.username}! Aguardando jogadores...")
        print("-" * 50)
        
        # Inicia a interface de input
        client.start_interface()
    else:
        print("\n❌ Não foi possível conectar ao servidor.")
        input("Pressione ENTER para sair.")