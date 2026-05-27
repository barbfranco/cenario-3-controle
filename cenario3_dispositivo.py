import socket
import json
import sys

HOST = "127.0.0.1"
PORTA = 5050

APELIDOS_DISPOSITIVOS = {
    "lampada-a": "lampada-amarela",
    "lampada-b": "lampada-branca",
    "motor-g": "motor-grande",
    "motor-p": "motor-pequeno",
}


def enviar_json(conexao, dados):
    # Envia um dicionario no formato JSON pela conexao.
    mensagem = json.dumps(dados) + "\n"
    conexao.sendall(mensagem.encode("utf-8"))


def nome_dispositivo(nome):
    # Converte apelidos curtos para os nomes completos dos dispositivos.
    return APELIDOS_DISPOSITIVOS.get(nome, nome)


def executar_comando(comando, estado):
    # Executa o comando recebido e devolve o novo estado com uma mensagem.
    if comando == "ligar":
        if estado == "ligado":
            return estado, "Esse dispositivo ja esta ligado."
        return "ligado", "Dispositivo ligado."

    if comando == "desligar":
        if estado == "desligado":
            return estado, "Esse dispositivo ja esta desligado."
        return "desligado", "Dispositivo desligado."

    if comando == "status":
        return estado, f"Dispositivo esta {estado}."

    return estado, "Comando desconhecido."


def main():
    # Define o nome do dispositivo usando o argumento do terminal.
    dispositivo_id = "lampada-amarela"
    if len(sys.argv) > 1:
        dispositivo_id = nome_dispositivo(sys.argv[1].lower())

    estado = "desligado"

    # Conecta o dispositivo ao servidor e informa seu identificador.
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((HOST, PORTA))
    enviar_json(cliente, {"tipo": "dispositivo", "id": dispositivo_id})

    print(f"Dispositivo {dispositivo_id} conectado ao servidor.")
    print("Aguardando comandos: ligar, desligar, status.")

    try:
        # Aguarda comandos enviados pelo servidor.
        arquivo = cliente.makefile("r", encoding="utf-8")
        for linha in arquivo:
            dados = json.loads(linha)

            if dados.get("tipo") != "comando":
                continue

            comando = dados.get("comando")
            estado, mensagem = executar_comando(comando, estado)

            print(f"Comando recebido: {comando} | {mensagem} Estado atual: {estado}")
            enviar_json(cliente, {
                "tipo": "resposta",
                "comando": comando,
                "estado": estado,
                "mensagem": mensagem,
            })

    except (ConnectionError, json.JSONDecodeError, OSError):
        print("Conexao encerrada.")
    finally:
        cliente.close()


if __name__ == "__main__":
    main()
