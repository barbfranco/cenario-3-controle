import socket
import threading
import json
import time

HOST = "127.0.0.1"
PORTA = 5050

dispositivos = {}
paineis = []
lock = threading.Lock()

APARELHOS_VALIDOS = ("alexa", "cafeteira", "aspirador")


def enviar_json(conexao, dados):
    # Envia dados em JSON para um cliente conectado.
    mensagem = json.dumps(dados) + "\n"
    conexao.sendall(mensagem.encode("utf-8"))


def enviar_log(texto):
    # Mostra uma mensagem no servidor e envia essa mensagem aos paineis.
    print(texto)
    pacote = {"tipo": "log", "mensagem": texto}

    with lock:
        paineis_conectados = list(paineis)

    for painel in paineis_conectados:
        try:
            enviar_json(painel, pacote)
        except OSError:
            with lock:
                if painel in paineis:
                    paineis.remove(painel)


def montar_lista_status():
    # Monta o bloco com o status de todos os aparelhos conectados.
    linhas = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "STATUS DE TODOS OS DISPOSITIVOS",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    with lock:
        aparelhos_conectados = {
            dispositivo_id: dados.get("status_formatado", "status nao informado")
            for dispositivo_id, dados in dispositivos.items()
        }

    for aparelho in APARELHOS_VALIDOS:
        if aparelho in aparelhos_conectados:
            linhas.append(aparelhos_conectados[aparelho])

    if len(linhas) == 3:
        linhas.append("Nenhum dispositivo conectado.")

    return "\n".join(linhas)


def encaminhar_para_dispositivo(dispositivo_id, comando):
    # Procura o dispositivo e repassa o comando recebido do painel.
    with lock:
        dispositivo = dispositivos.get(dispositivo_id)

    if dispositivo is None:
        enviar_log(f"[ERRO] Dispositivo '{dispositivo_id}' nao encontrado.")
        return

    try:
        enviar_json(dispositivo["conexao"], {"tipo": "comando", "comando": comando})
        enviar_log(f"[COMANDO] {comando} enviado para {dispositivo_id}.")
    except OSError:
        enviar_log(f"[ERRO] Falha ao enviar comando para {dispositivo_id}.")


def tratar_dispositivo(conexao, endereco, primeira_msg):
    # Mantem a comunicacao com um dispositivo conectado.
    dispositivo_id = primeira_msg.get("id", f"{endereco[0]}:{endereco[1]}")

    if dispositivo_id not in APARELHOS_VALIDOS:
        enviar_json(conexao, {"tipo": "erro", "mensagem": "Aparelho desconhecido."})
        conexao.close()
        return

    with lock:
        dispositivos[dispositivo_id] = {
            "conexao": conexao,
            "endereco": endereco,
            "estado": primeira_msg.get("estado", "desligado"),
            "status_formatado": primeira_msg.get("status_formatado", ""),
        }

    enviar_log(f"[CONECTADO] Dispositivo {dispositivo_id} em {endereco}.")

    try:
        arquivo = conexao.makefile("r", encoding="utf-8")
        for linha in arquivo:
            dados = json.loads(linha)

            if dados.get("tipo") == "resposta":
                comando = dados.get("comando", "")
                mensagem = dados.get("mensagem", "")
                status_formatado = dados.get("status_formatado", "")
                with lock:
                    if dispositivo_id in dispositivos:
                        dispositivos[dispositivo_id]["estado"] = dados.get("estado", "")
                        dispositivos[dispositivo_id]["status_formatado"] = status_formatado
                enviar_log(f"[RESPOSTA] {comando}: {mensagem} {status_formatado}")

    except (ConnectionError, json.JSONDecodeError, OSError):
        enviar_log(f"[DESCONECTADO] Dispositivo {dispositivo_id}.")
    finally:
        with lock:
            if dispositivos.get(dispositivo_id, {}).get("conexao") is conexao:
                del dispositivos[dispositivo_id]
        conexao.close()


def tratar_painel(conexao, endereco):
    # Recebe comandos do painel e decide o que fazer com cada um.
    with lock:
        paineis.append(conexao)

    enviar_log(f"[CONECTADO] Painel em {endereco}.")
    enviar_json(conexao, {"tipo": "log", "mensagem": "Painel conectado ao servidor."})
    enviar_json(conexao, {"tipo": "log", "mensagem": "Use: ligar <id>, desligar <id>, status <id> ou lista"})
    enviar_json(conexao, {"tipo": "log", "mensagem": "Aparelhos: alexa 🔊, cafeteira ☕, aspirador 🤖"})

    try:
        arquivo = conexao.makefile("r", encoding="utf-8")
        for linha in arquivo:
            dados = json.loads(linha)

            if dados.get("tipo") != "painel":
                continue

            comando = dados.get("comando", "").strip().lower()
            partes = comando.split()

            if comando == "lista":
                enviar_json(conexao, {"tipo": "log", "mensagem": montar_lista_status()})
                continue

            if len(partes) != 2 or partes[0] not in ("ligar", "desligar", "status"):
                enviar_json(conexao, {"tipo": "log", "mensagem": "Comando invalido. Use: ligar <id>, desligar <id>, status <id> ou lista"})
                continue

            acao, dispositivo_id = partes

            if dispositivo_id not in APARELHOS_VALIDOS:
                enviar_json(conexao, {"tipo": "log", "mensagem": "Aparelho invalido. Use: alexa, cafeteira ou aspirador."})
                continue

            encaminhar_para_dispositivo(dispositivo_id, acao)

    except (ConnectionError, json.JSONDecodeError, OSError):
        enviar_log(f"[DESCONECTADO] Painel {endereco}.")
    finally:
        with lock:
            if conexao in paineis:
                paineis.remove(conexao)
        conexao.close()


def tratar_cliente(conexao, endereco):
    # Identifica se o cliente conectado e painel ou dispositivo.
    try:
        arquivo = conexao.makefile("r", encoding="utf-8")
        primeira_linha = arquivo.readline()
        if not primeira_linha:
            conexao.close()
            return

        primeira_msg = json.loads(primeira_linha)
        tipo = primeira_msg.get("tipo")

        if tipo == "dispositivo":
            tratar_dispositivo(conexao, endereco, primeira_msg)
        elif tipo == "painel":
            tratar_painel(conexao, endereco)
        else:
            enviar_json(conexao, {"tipo": "erro", "mensagem": "Tipo de cliente desconhecido."})
            conexao.close()

    except (ConnectionError, json.JSONDecodeError, OSError):
        conexao.close()


def main():
    # Inicia o servidor e cria uma thread para cada cliente conectado.
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORTA))
    servidor.listen()

    print(f"Servidor iniciado em {HOST}:{PORTA}")
    print("Aguardando dispositivos e painel...")

    try:
        while True:
            conexao, endereco = servidor.accept()
            thread = threading.Thread(target=tratar_cliente, args=(conexao, endereco))
            thread.daemon = True
            thread.start()
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        servidor.close()


if __name__ == "__main__":
    main()
