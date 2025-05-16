import pika
import pickle
import networkx as nx
import random
from collections import deque
from multiprocessing import Process, Queue
import time
"""
Aquie tenemos los generadores de laberintos y sudokus
Los laberintos son generados usando un algoritmo de BFS y los sudokus son generados usando backtracking"""
# --- Generador de Laberinto ---
def generar_laberinto(filas, columnas):
    G = nx.Graph()
    for i in range(filas):
        for j in range(columnas):
            G.add_node((i, j))

    start = (0, 0)
    visitados = set([start])
    queue = deque([start])

    while queue:
        actual = queue.popleft()
        vecinos = [(actual[0]+dx, actual[1]+dy) for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]]
        random.shuffle(vecinos)
        for vecino in vecinos:
            if 0 <= vecino[0] < filas and 0 <= vecino[1] < columnas and vecino not in visitados:
                G.add_edge(actual, vecino)
                visitados.add(vecino)
                queue.append(vecino)
    return G
# --- Generador de Sudoku ---
def generar_sudoku():
    dificultad = random.choice(['facil', 'normal', 'dificil'])
    sudoku = [[0 for _ in range(9)] for _ in range(9)]

    def rellenar_bloque(bloque):
        nums = list(range(1, 10))
        random.shuffle(nums)
        for i in range(3):
            for j in range(3):
                sudoku[bloque*3 + i][bloque*3 + j] = nums.pop()

    for bloque in range(3):
        rellenar_bloque(bloque)

    def es_valido(fila, col, num):
        for i in range(9):
            if sudoku[fila][i] == num or sudoku[i][col] == num:
                return False
        start_row, start_col = 3 * (fila // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if sudoku[start_row + i][start_col + j] == num:
                    return False
        return True

    def resolver():
        for i in range(9):
            for j in range(9):
                if sudoku[i][j] == 0:
                    for num in range(1, 10):
                        if es_valido(i, j, num):
                            sudoku[i][j] = num
                            if resolver():
                                return True
                            sudoku[i][j] = 0
                    return False
        return True

    resolver()

    if dificultad == 'facil':
        celdas_a_eliminar = random.randint(30, 35)
    elif dificultad == 'normal':
        celdas_a_eliminar = random.randint(40, 50)
    else:
        celdas_a_eliminar = random.randint(55, 60)

    eliminadas = 0
    while eliminadas < celdas_a_eliminar:
        i, j = random.randint(0, 8), random.randint(0, 8)
        if sudoku[i][j] != 0:
            sudoku[i][j] = 0
            eliminadas += 1

    return {'sudoku': sudoku, 'dificultad': dificultad}
"""
Aqui tenemos los workers que hacen es generar los laberintos y sudokus en paralelo
"""
# --- Worker: Laberinto ---
def worker_laberinto(q, worker_id, num_items):
    for i in range(num_items):
        lab = generar_laberinto(random.randint(5, 80), random.randint(5, 80))
        q.put(pickle.dumps(lab))
        print(f"[GEN-LAB-{worker_id}] Laberinto {i+1}/{num_items} generado")
        time.sleep(0.2)
    q.put(None)  # Señal de fin para publisher
# --- Worker: Sudoku ---
def worker_sudoku(q, worker_id, num_items):
    for i in range(num_items):
        sudoku = generar_sudoku()
        q.put(pickle.dumps(sudoku))
        print(f"[GEN-SUDOKU-{worker_id}] Sudoku {i+1}/{num_items} generado")
        time.sleep(0.2)
    q.put(None)  # Señal de fin para publisher
"""
Publicar Este es el publisher que se encarga de enviar los laberintos y sudokus a RabbitMQ
"""
# --- Publisher: Sudoku ---
def publisher_sudoku(q, num_workers):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='noticias_direct', exchange_type='direct')

    finished_workers = 0
    while finished_workers < num_workers:
        sudoku_serializado = q.get()  # Bloqueante
        if sudoku_serializado is None:
            finished_workers += 1
            print(f"[PUBLISHER-SUDOKU] Recibida señal de fin de worker ({finished_workers}/{num_workers})")
            continue
        channel.basic_publish(exchange='noticias_direct', routing_key='sudoku', body=sudoku_serializado)
        print("[PUBLISHER-SUDOKU] Sudoku enviado")

    connection.close()
    print("[PUBLISHER-SUDOKU] Todos los sudokus publicados.")
# --- Publisher: Laberinto ---
def publisher_laberinto(q, num_workers):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='noticias_direct', exchange_type='direct')

    finished_workers = 0
    while finished_workers < num_workers:
        lab_serializado = q.get()  # Bloqueante
        if lab_serializado is None:
            finished_workers += 1
            print(f"[PUBLISHER-LAB] Recibida señal de fin de worker ({finished_workers}/{num_workers})")
            continue
        channel.basic_publish(exchange='noticias_direct', routing_key='laberinto', body=lab_serializado)
        print("[PUBLISHER-LAB] Laberinto enviado")

    connection.close()
    print("[PUBLISHER-LAB] Todos los laberintos publicados.")


"""
Aqui es donde se ejecutan los workers y el publisher que trabajan en paralelo los workers generan los laberintos y sudokus 
y se lo envian al publisher para que los envie a RabbitMQ
"""
def main_laberinto(total_items=50):
    q = Queue()
    num_workers = 10
    items_per_worker = total_items//num_workers

    workers = [Process(target=worker_laberinto, args=(q, i+1, items_per_worker)) for i in range(num_workers)]
    #los workers generan laberintos en paralelo
    #mandamos los laberintos a la cola para que el publisher los envie
    publisher = Process(target=publisher_laberinto, args=(q, num_workers))

    for w in workers:
        w.start()
    publisher.start()

    for w in workers:
        w.join()
    publisher.join()


def main_sudoku(total_items=50):
    q = Queue()
    num_workers = 10
    items_per_worker = total_items//num_workers

    workers = [Process(target=worker_sudoku, args=(q, i+1, items_per_worker)) for i in range(num_workers)]
    #empezamos los workers para que vayan generando los sudokus
    publisher = Process(target=publisher_sudoku, args=(q, num_workers))
    #empezamos el publisher para que vayan enviando los sudokus
    for w in workers:
        w.start()
    publisher.start()

    for w in workers:
        w.join()
    publisher.join()
    #vamos mandando los sudokus a la cola para que el publisher los envie

"""Ejecucion en paralelo creando dos diferentes procesos que van generando y procesando laberintos y sudokus"""
if __name__ == '__main__':
    N = 50  # Total de laberintos y sudokus a generar
    p1 = Process(target=main_laberinto, args=(N,))
    p2 = Process(target=main_sudoku, args=(N,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
