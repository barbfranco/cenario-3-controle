import socket
import threading
import json

HOST = "127.0.0.1"
PORTA = 5050


def enviar_json(conexao, dados):
    # Envia um comando ou identificacao em formato JSON.
    mensagem = json.dumps(dados) + "\n"
    conexao.sendall(mensagem.encode("utf-8"))


def receber_logs(conexao):
    # Recebe mensagens do servidor e mostra no painel.
    try:
        arquivo = conexao.makefile("r", encoding="utf-8")
        for linha in arquivo:
            dados = json.loads(linha)
            if dados.get("tipo") == "log":
                print(dados.get("mensagem", ""))
    except (ConnectionError, json.JSONDecodeError, OSError):
        print("Conexao com o servidor encerrada.")


def ajustar_comando(comando):
    # Padroniza o comando digitado antes de enviar ao servidor.
    partes = comando.strip().lower().split()
    if len(partes) == 2:
        return " ".join(partes)
    return comando.strip().lower()


def main():
    # Conecta o painel ao servidor.
    painel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    painel.connect((HOST, PORTA))
    enviar_json(painel, {"tipo": "painel"})

    # Cria uma thread para receber logs enquanto o usuario digita comandos.
    thread = threading.Thread(target=receber_logs, args=(painel,))
    thread.daemon = True
    thread.start()

    print("Painel de controle remoto")
    print("Aparelhos: alexa 🔊 | cafeteira ☕ | aspirador 🤖")
    print("Comandos: lista | ligar <id> | desligar <id> | status <id> | sair")

    try:
        # Le comandos digitados pelo usuario e envia para o servidor.
        while True:
            comando = input("> ").strip()

            if comando.lower() == "sair":
                break

            if comando:
                enviar_json(painel, {"tipo": "painel", "comando": ajustar_comando(comando)})

    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        painel.close()
        print("Painel encerrado.")


if __name__ == "__main__":
    main()
