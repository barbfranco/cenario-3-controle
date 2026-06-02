import socket
import json
import sys

HOST = "127.0.0.1"
PORTA = 5050

DISPOSITIVOS = {
    "alexa": {
        "nome": "Alexa",
        "emoji": "🔊",
        "ligado": "LIGADA",
        "desligado": "DESLIGADA",
    },
    "cafeteira": {
        "nome": "Cafeteira",
        "emoji": "☕",
        "ligado": "LIGADA",
        "desligado": "DESLIGADA",
    },
    "aspirador": {
        "nome": "Robô Aspirador",
        "emoji": "🤖",
        "ligado": "LIGADO",
        "desligado": "DESLIGADO",
    },
}


def enviar_json(conexao, dados):
    # Envia um dicionario no formato JSON pela conexao.
    mensagem = json.dumps(dados) + "\n"
    conexao.sendall(mensagem.encode("utf-8"))


def dados_dispositivo(dispositivo_id):
    # Busca as informacoes visuais do dispositivo escolhido.
    return DISPOSITIVOS.get(dispositivo_id, {
        "nome": dispositivo_id.title(),
        "emoji": "📱",
        "ligado": "LIGADO",
        "desligado": "DESLIGADO",
    })


def linha_status(dispositivo_id, estado):
    # Monta a linha de status com emoji, nome e estado atual.
    dispositivo = dados_dispositivo(dispositivo_id)
    emoji_estado = "🟢" if estado == "ligado" else "🔴"
    texto_estado = dispositivo[estado]
    return f"{dispositivo['emoji']} {dispositivo['nome']} -> {emoji_estado} {texto_estado}"


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
    dispositivo_id = "alexa"
    if len(sys.argv) > 1:
        dispositivo_id = sys.argv[1].lower()

    estado = "desligado"
    dispositivo = dados_dispositivo(dispositivo_id)

    # Conecta o dispositivo ao servidor e informa seu identificador.
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((HOST, PORTA))
    enviar_json(cliente, {
        "tipo": "dispositivo",
        "id": dispositivo_id,
        "estado": estado,
        "status_formatado": linha_status(dispositivo_id, estado),
    })

    print(f"{dispositivo['emoji']} {dispositivo['nome']} conectado ao servidor.")
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
            status_formatado = linha_status(dispositivo_id, estado)

            print(f"Comando recebido: {comando} | {mensagem} {status_formatado}")
            enviar_json(cliente, {
                "tipo": "resposta",
                "comando": comando,
                "estado": estado,
                "mensagem": mensagem,
                "status_formatado": status_formatado,
            })

    except (ConnectionError, json.JSONDecodeError, OSError):
        print("Conexao encerrada.")
    finally:
        cliente.close()


if __name__ == "__main__":
    main()
