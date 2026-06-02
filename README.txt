Cenario 3 - Controle remoto de aparelhos

Arquivos:
- cenario3_servidor.py: servidor TCP que recebe aparelhos e painel.
- cenario3_dispositivo.py: cliente que simula Alexa, cafeteira ou robo aspirador.
- cenario3_painel.py: cliente especial que envia comandos e mostra os logs.

Como executar:

1. Abra um terminal e rode o servidor:
   python cenario3_servidor.py

2. Abra outro terminal e rode um dispositivo:
   python cenario3_dispositivo.py alexa

3. Abra outros terminais para os demais aparelhos:
   python cenario3_dispositivo.py cafeteira
   python cenario3_dispositivo.py aspirador

4. Abra outro terminal e rode o painel:
   python cenario3_painel.py

Comandos no painel:
- lista
- ligar alexa
- desligar alexa
- status cafeteira
- ligar aspirador
- status aspirador
- sair

Aparelhos aceitos:
- alexa 🔊
- cafeteira ☕
- aspirador 🤖

Ao usar o comando "lista", o painel mostra o status de todos os aparelhos conectados.

O painel mostra os comandos enviados e as respostas recebidas dos aparelhos.
Se um aparelho ja estiver ligado e receber "ligar", ele avisa que ja esta ligado.
Se ja estiver desligado e receber "desligar", ele avisa que ja esta desligado.