import socket
import json
import sys

HOST = "127.0.0.1"
PORTA = 5050


def enviar_json(conexao, dados):
    mensagem = json.dumps(dados) + "\n"
    conexao.sendall(mensagem.encode("utf-8"))


def main():
    dispositivo_id = "lampada1"
    if len(sys.argv) > 1:
        dispositivo_id = sys.argv[1]

    estado = "desligado"

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((HOST, PORTA))
    enviar_json(cliente, {"tipo": "dispositivo", "id": dispositivo_id})

    print(f"Dispositivo {dispositivo_id} conectado ao servidor.")
    print("Aguardando comandos: ligar, desligar, status.")

    try:
        arquivo = cliente.makefile("r", encoding="utf-8")
        for linha in arquivo:
            dados = json.loads(linha)

            if dados.get("tipo") != "comando":
                continue

            comando = dados.get("comando")

            if comando == "ligar":
                estado = "ligado"
            elif comando == "desligar":
                estado = "desligado"
            elif comando == "status":
                pass
            else:
                comando = "comando desconhecido"

            print(f"Comando recebido: {comando} | Estado atual: {estado}")
            enviar_json(cliente, {"tipo": "resposta", "comando": comando, "estado": estado})

    except (ConnectionError, json.JSONDecodeError, OSError):
        print("Conexao encerrada.")
    finally:
        cliente.close()


if __name__ == "__main__":
    main()
