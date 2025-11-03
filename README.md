
# Jogo da Forca Cooperativo

Projeto desenvolvido para a disciplina **Redes de Computadores** da Universidade Federal de Alagoas (UFAL), sob orientação do professor **Almir Pereira Guimarães**.

O objetivo é implementar um **jogo da forca em rede**, no formato **cliente-servidor**, utilizando **Python**, **sockets TCP/IP** e **threads** para permitir a interação simultânea entre múltiplos jogadores de forma cooperativa.

---

## Integrantes do grupo
- Nelson Alves Sousa Moreira  
- Francys Samuel Oliveira Pereira dos Santos  
- Morgana Cavalcante Batista  
- Marta Mirely Nascimento dos Santos  

---

## Tecnologias utilizadas
- **Python 3.12+**
- **Bibliotecas padrão**: `socket`, `threading`, `sys`

---

## Conceitos aplicados
- Comunicação cliente-servidor via **sockets TCP**
- **Multithreading** para suportar vários clientes simultaneamente
- **Protocolo textual** simples para troca de mensagens entre cliente e servidor
- **Sincronização de estados** do jogo entre os jogadores conectados

---

## Como executar o projeto

### 1. Clonar o repositório
```bash
git clone https://github.com/nelsonalvs/forca-cooperativa.git
cd forca-cooperativa
```

### 2. Executar o servidor
Em um terminal, rode:
```bash
python server.py
```
> O servidor ficará escutando conexões em uma porta específica (por padrão, `localhost:5000`).

### 3. Executar os clientes
Em outros terminais (ou outras máquinas da mesma rede local):
```bash
python client.py
```

Ao iniciar, o cliente se conecta ao servidor e aguarda o início do jogo.  
Cada jogador envia suas tentativas de letras, e o servidor coordena os turnos e atualiza o estado do jogo para todos.

---

## Protocolo de mensagens

A comunicação é feita via mensagens textuais padronizadas, por exemplo:

| Tipo de mensagem | Exemplo | Descrição |
|------------------|----------|-----------|
| `START:palavra:oculta:tentativas:tema` | `START:maçã:_ _ _ ã:6:Frutas` | Início de nova rodada |
| `TURN:usuario` | `TURN:Jogador1` | Indica o turno do jogador |
| `CORRECT:letra:palavra_atualizada` | `CORRECT:a:_ a _ a` | Letra correta |
| `WRONG:letra:tentativas_restantes` | `WRONG:x:4` | Letra incorreta |
| `WIN:palavra:tema` | `WIN:maçã:Frutas` | Fim do jogo (vitória) |

---

## Dificuldades encontradas
Durante o desenvolvimento, enfrentamos desafios como:
- Sincronização correta dos turnos entre jogadores;
- Tratamento de desconexões inesperadas de clientes;
- Reinício automático do jogo ao término de uma rodada;
- Testes em diferentes sistemas operacionais e redes locais.

---

## Possíveis melhorias
- Interface gráfica para o cliente (ex: com Tkinter ou PyQt);
- Suporte a múltiplas salas de jogo simultâneas;
- Sistema de pontuação e ranking entre jogadores.

---

## Referências
- [Documentação oficial da biblioteca `socket`](https://docs.python.org/3/library/socket.html)
- Materiais da disciplina **Redes de Computadores – UFAL (2025)**

---

## Informações acadêmicas
**Disciplina:** Redes de Computadores  
**Professor:** Almir Pereira Guimarães  
**Instituição:** Universidade Federal de Alagoas (UFAL)  
**Período:** 2025.1  
