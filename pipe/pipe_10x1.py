"""

Cenario: comunicacao de dez processos com um processo via pipe
10 processos remetente escrevem para outro 1 processo destinatario, que le e exibe as mensagens

"""

from multiprocessing import Pipe, Process, Lock
from os import getpid
from time import time
import psutil

# Recebe dados do processo remetente via pipe
def leitura(r, w, lock):
    # Fecha a escrita no pipe
    w.close()

    # Faz a leitura para cada um dos 10 processos de remetente
    for _ in range(10):
        # Fecha trava para que a mensagem não seja alterada antes do print
        lock.acquire()

        # Recebe mensagem, a exibe no terminal junto com seu PID e calcula tempo de comunicacao
        t = time()
        mensagem = r.recv()
        print("Tempo de recebimento: %s" % (time() - t))
        print("Processo %s recebeu: %s" % (getpid(), mensagem))

        # Abre trava
        lock.release()

    # Fecha a leitura do pipe
    r.close()

    # Calcula uso de memoria do processo
    p = psutil.Process(getpid())
    print("Destinatario:", p.memory_info())

# Envia dados para o processo destinatario via pipe
def escrita(r, w, lock):
    # Fecha a leitura do pipe
    r.close()

    # Fecha trava para que a mensagem nao seja alterada antes de ser enviada
    lock.acquire()

    # Define mensagem contendo seu PID, a envia e calcula tempo de comunicacao
    mensagem = "\"Saudacoes do processo %s!\"" % getpid()
    t = time()
    w.send(mensagem)
    print("Tempo de envio: %s" % (time() - t))

    # Abre trava
    lock.release()

    # Fecha a escrita no pipe
    w.close()

    # Calcula uso de memoria do processo
    p = psutil.Process(getpid())
    print("Remetente:", p.memory_info())

# Realiza a comunicacao via pipe de 10 processos com outro processo
def main():
    # Cria o pipe e a trava usada para exclusao mutua na regiao critica
    r, w = Pipe()
    lock = Lock()

    # Cria processos e atribui a cada um a funcao que executarao
    remetente = []
    for _ in range(10):
        p = Process(target=escrita, args=(r, w, lock))
        remetente.append(p)

    destinatario = Process(target=leitura, args=(r, w, lock))

    # Inicia a execucao dos processos e faz processo pai aguardar o termino de execucao dos mesmos
    for p in remetente:
        p.start()
        p.join()

    destinatario.start()
    destinatario.join()

if __name__ == '__main__':
    main()