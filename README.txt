Cenario 3 - Controle remoto de dispositivos

Arquivos:
- cenario3_servidor.py: servidor TCP que recebe dispositivos e painel.
- cenario3_dispositivo.py: cliente que simula uma lampada, motor ou outro dispositivo.
- cenario3_painel.py: cliente especial que envia comandos e mostra os logs.

Como executar:

1. Abra um terminal e rode o servidor:
   python cenario3_servidor.py

2. Abra outro terminal e rode um dispositivo:
   python cenario3_dispositivo.py lampada-amarela

3. Abra outros terminais para os demais dispositivos:
   python cenario3_dispositivo.py lampada-branca
   python cenario3_dispositivo.py motor-grande
   python cenario3_dispositivo.py motor-pequeno

4. Abra outro terminal e rode o painel:
   python cenario3_painel.py

Comandos no painel:
- lista
- ligar lampada-amarela
- desligar lampada-amarela
- status lampada-branca
- ligar motor-grande
- status motor-pequeno
- sair

Atalhos aceitos no painel:
- lampada-a = lampada-amarela
- lampada-b = lampada-branca
- motor-g = motor-grande
- motor-p = motor-pequeno

Tambem e possivel usar os atalhos ao iniciar um dispositivo:
- python cenario3_dispositivo.py lampada-a
- python cenario3_dispositivo.py motor-g

O painel mostra os comandos enviados e as respostas recebidas dos dispositivos.
Se um dispositivo ja estiver ligado e receber "ligar", ele avisa que ja esta ligado.
Se ja estiver desligado e receber "desligar", ele avisa que ja esta desligado.
