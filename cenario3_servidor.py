import socket
import threading
import json
import time

HOST = "127.0.0.1"
PORTA = 5050

dispositivos = {}
paineis = []
lock = threading.Lock()


def enviar_json(conexao, dados):
    mensagem = json.dumps(dados) + "\n"
    conexao.sendall(mensagem.encode("utf-8"))


def enviar_log(texto):
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


def encaminhar_para_dispositivo(dispositivo_id, comando):
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
    dispositivo_id = primeira_msg.get("id", f"{endereco[0]}:{endereco[1]}")

    with lock:
        dispositivos[dispositivo_id] = {"conexao": conexao, "endereco": endereco}

    enviar_log(f"[CONECTADO] Dispositivo {dispositivo_id} em {endereco}.")

    try:
        arquivo = conexao.makefile("r", encoding="utf-8")
        for linha in arquivo:
            dados = json.loads(linha)

            if dados.get("tipo") == "resposta":
                comando = dados.get("comando", "")
                estado = dados.get("estado", "")
                enviar_log(f"[RESPOSTA] {dispositivo_id} respondeu '{comando}': estado atual = {estado}.")

    except (ConnectionError, json.JSONDecodeError, OSError):
        enviar_log(f"[DESCONECTADO] Dispositivo {dispositivo_id}.")
    finally:
        with lock:
            if dispositivos.get(dispositivo_id, {}).get("conexao") is conexao:
                del dispositivos[dispositivo_id]
        conexao.close()


def tratar_painel(conexao, endereco):
    with lock:
        paineis.append(conexao)

    enviar_log(f"[CONECTADO] Painel em {endereco}.")
    enviar_json(conexao, {"tipo": "log", "mensagem": "Painel conectado ao servidor."})
    enviar_json(conexao, {"tipo": "log", "mensagem": "Use: ligar <id>, desligar <id>, status <id> ou lista"})

    try:
        arquivo = conexao.makefile("r", encoding="utf-8")
        for linha in arquivo:
            dados = json.loads(linha)

            if dados.get("tipo") != "painel":
                continue

            comando = dados.get("comando", "").strip().lower()
            partes = comando.split()

            if comando == "lista":
                with lock:
                    nomes = ", ".join(dispositivos.keys()) or "nenhum dispositivo conectado"
                enviar_json(conexao, {"tipo": "log", "mensagem": f"Dispositivos: {nomes}"})
                continue

            if len(partes) != 2 or partes[0] not in ("ligar", "desligar", "status"):
                enviar_json(conexao, {"tipo": "log", "mensagem": "Comando invalido. Use: ligar <id>, desligar <id>, status <id> ou lista"})
                continue

            acao, dispositivo_id = partes
            encaminhar_para_dispositivo(dispositivo_id, acao)

    except (ConnectionError, json.JSONDecodeError, OSError):
        enviar_log(f"[DESCONECTADO] Painel {endereco}.")
    finally:
        with lock:
            if conexao in paineis:
                paineis.remove(conexao)
        conexao.close()


def tratar_cliente(conexao, endereco):
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
