import socket
import threading
import json

HOST = "127.0.0.1"
PORTA = 5050


def enviar_json(conexao, dados):
    mensagem = json.dumps(dados) + "\n"
    conexao.sendall(mensagem.encode("utf-8"))


def receber_logs(conexao):
    try:
        arquivo = conexao.makefile("r", encoding="utf-8")
        for linha in arquivo:
            dados = json.loads(linha)
            if dados.get("tipo") == "log":
                print(dados.get("mensagem", ""))
    except (ConnectionError, json.JSONDecodeError, OSError):
        print("Conexao com o servidor encerrada.")


def main():
    painel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    painel.connect((HOST, PORTA))
    enviar_json(painel, {"tipo": "painel"})

    thread = threading.Thread(target=receber_logs, args=(painel,))
    thread.daemon = True
    thread.start()

    print("Painel de controle remoto")
    print("Comandos: lista | ligar <id> | desligar <id> | status <id> | sair")

    try:
        while True:
            comando = input("> ").strip()

            if comando.lower() == "sair":
                break

            if comando:
                enviar_json(painel, {"tipo": "painel", "comando": comando})

    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        painel.close()
        print("Painel encerrado.")


if __name__ == "__main__":
    main()
