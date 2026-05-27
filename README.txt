Cenario 3 - Controle remoto de dispositivos

Arquivos:
- cenario3_servidor.py: servidor TCP que recebe dispositivos e painel.
- cenario3_dispositivo.py: cliente que simula uma lampada, motor ou outro dispositivo.
- cenario3_painel.py: cliente especial que envia comandos e mostra os logs.

Como executar:

1. Abra um terminal e rode o servidor:
   python cenario3_servidor.py

2. Abra outro terminal e rode um dispositivo:
   python cenario3_dispositivo.py lampada1

3. Opcionalmente, abra outro terminal com mais um dispositivo:
   python cenario3_dispositivo.py motor1

4. Abra outro terminal e rode o painel:
   python cenario3_painel.py

Comandos no painel:
- lista
- ligar lampada1
- desligar lampada1
- status lampada1
- ligar motor1
- status motor1
- sair

O painel mostra os comandos enviados e as respostas recebidas dos dispositivos.
