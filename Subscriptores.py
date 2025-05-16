import pika
import pickle
import networkx as nx
import matplotlib.pyplot as plt
import time
import signal
import sys

# --- Variables globales para estadísticas ---
contador = 0
tiempo_total = 0.0
"""
Aqui los subscriptores resuelven los laberintos y sudokus que les envian
y los dibujan
Los laberintos son representados como grafos y los sudokus como matrices
Los laberintos son resueltos usando DFS y los sudokus usando backtracking
"""
# --- Resolver Laberinto (DFS) ---
def resolver_laberinto(grafo, inicio=(0, 0), fin=None):
    if fin is None:
        fin = max(grafo.nodes)
    camino = []
    visitados = set()

    def dfs(nodo):
        if nodo == fin:
            camino.append(nodo)
            return True
        visitados.add(nodo)
        for vecino in grafo.neighbors(nodo):
            if vecino not in visitados:
                if dfs(vecino):
                    camino.append(nodo)
                    return True
        return False

    if dfs(inicio):
        return list(reversed(camino))
    else:
        return []

# --- Dibujar Laberinto ---
def dibujar_laberinto(grafo, camino):
    pos = {n: (n[1], -n[0]) for n in grafo.nodes}
    plt.figure(figsize=(8, 8))
    nx.draw(grafo, pos, node_size=20, with_labels=False, node_color='lightgray', edge_color='gray')
    if camino:
        camino_edges = list(zip(camino[:-1], camino[1:]))
        nx.draw_networkx_edges(grafo, pos, edgelist=camino_edges, edge_color='red', width=2)
        nx.draw_networkx_nodes(grafo, pos, nodelist=camino, node_color='red', node_size=30)
    plt.title("Laberinto resuelto (camino en rojo)")
    plt.axis('off')
    plt.show()

# --- Resolver Sudoku (Backtracking) ---
def resolver_sudoku(tablero):
    def es_valido(fila, col, num):
        for i in range(9):
            if tablero[fila][i] == num or tablero[i][col] == num:
                return False
        start_row, start_col = 3 * (fila // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if tablero[start_row + i][start_col + j] == num:
                    return False
        return True

    def backtrack():
        for i in range(9):
            for j in range(9):
                if tablero[i][j] == 0:
                    for num in range(1, 10):
                        if es_valido(i, j, num):
                            tablero[i][j] = num
                            if backtrack():
                                return True
                            tablero[i][j] = 0
                    return False
        return True

    return backtrack()

# --- Dibujar Sudoku ---
def dibujar_sudoku(tablero_resuelto, tablero_original=None):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xticks([x - 0.5 for x in range(1, 9)], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, 9)], minor=True)
    ax.grid(which='minor', color='black', linewidth=1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-0.5, 8.5)
    ax.set_ylim(8.5, -0.5)

    for i in range(9):
        for j in range(9):
            num = tablero_resuelto[i][j]
            if num != 0:
                color = 'black'
                if tablero_original and tablero_original[i][j] == 0:
                    color = 'red'
                ax.text(j, i, str(num), ha='center', va='center', fontsize=14, color=color)

    for i in range(1, 9):
        lw = 2 if i % 3 == 0 else 0.5
        ax.axhline(i - 0.5, color='black', linewidth=lw)
        ax.axvline(i - 0.5, color='black', linewidth=lw)

    plt.title("Sudoku Resuelto (números nuevos en rojo)")
    plt.show()
"""
Como los datos estan en formato pickle, tenemos que inicializarlos y aque calsulamos el tiempo
de cada uno
Los laberintos y Los sudokus.
"""
# --- Callback Laberinto ---
def callback_laberinto(ch, method, properties, body):
    global contador, tiempo_total
    grafo = pickle.loads(body)
    start = time.time()
    camino = resolver_laberinto(grafo)
    duracion = time.time() - start
    contador += 1
    tiempo_total += duracion
    print(f"\n[SUB-LAB] Laberinto #{contador} resuelto en {duracion:.4f}s. Camino: {len(camino)} pasos.")
    dibujar_laberinto(grafo, camino)

# --- Callback Sudoku ---
def callback_sudoku(ch, method, properties, body):
    global contador, tiempo_total
    data = pickle.loads(body)
    tablero_original = [fila[:] for fila in data['sudoku']]
    dificultad = data['dificultad']
    start = time.time()
    exito = resolver_sudoku(data['sudoku'])
    duracion = time.time() - start
    contador += 1
    tiempo_total += duracion
    print(f"\n[SUB-SUDOKU] Sudoku #{contador} ({dificultad}) resuelto en {duracion:.4f}s. ¿Éxito?: {'Sí' if exito else 'No'}")
    if exito:
        dibujar_sudoku(data['sudoku'], tablero_original)

# Aqui imprimimos el resumen de los laberintos o sudokus
def imprimir_resumen(opcion):
    if contador == 0:
        print("\n[RESUMEN] No se resolvieron problemas.")
    else:
        promedio = tiempo_total / contador
        print(f"\n[RESUMEN] Total {opcion}s resueltos: {contador}")
        print(f"Tiempo total: {tiempo_total:.2f}s")
        print(f"Tiempo promedio: {promedio:.4f}s")
"""
Este main pregunta donde te vas a suscribir y
si es laberinto o sudoku
Conecta a RabbitMQ y se suscribe al canal correspondiente
Cuando estas suscrito, espera mensajes
y luego va recibiendo los mensajes
y los procesa
Resolviendolos y dibujandolos
"""
def main():
    
    while True:
        opcion = input("¿A qué deseas suscribirte? (laberinto / sudoku): ").strip().lower()
        if opcion in ['laberinto', 'sudoku']:
            break
        print("Opción inválida. Usa 'laberinto' o 'sudoku'.")

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='noticias_direct', exchange_type='direct')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='noticias_direct', queue=queue_name, routing_key=opcion)

    print(f"[SUB-{opcion.upper()}] Suscrito a '{opcion}'. Esperando mensajes...")

    # Enlace señal para resumen
    def detener_gracioso(sig, frame):# esto solo ocurre si el usuario presiona Ctrl+C   
        imprimir_resumen(opcion)
        sys.exit(0)

    signal.signal(signal.SIGINT, detener_gracioso)

    if opcion == 'laberinto':
        channel.basic_consume(queue=queue_name, on_message_callback=callback_laberinto, auto_ack=True)
    else:
        channel.basic_consume(queue=queue_name, on_message_callback=callback_sudoku, auto_ack=True)
    try:#para evitar que el programa se cierre si la conexion se pierde
        channel.start_consuming()
    except pika.exceptions.StreamLostError as e:
        print(f"[ERROR] Conexión perdida: {e}")
        imprimir_resumen(opcion)
        sys.exit(0)

if __name__ == '__main__':
    main()
