"""
UNJu - Facultad de Ingeniería
Teoría de Sistemas Operativos (TSO) - Ciclo Lectivo 2026
Cátedra: Ing. María Fernanda Vázquez - JTP: Ing. Fabio D. Argañaraz

Ejercicio Práctico N° 2: El Problema del Oso y las Abejas
Bibliografía de Referencia:
- Silberschatz: Cap. 6.6 (Problemas clásicos de sincronización)
- Stallings: Cap. 5.4 (Sincronización con semáforos)
"""

import sys
import threading
import time
import random

# Configuración UTF-8 para consola Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

M = 10                  # Capacidad del tarro de miel
NUM_ABEJAS = 5          # Número de abejas obreras
tarro_miel = 0          # Variable compartida
simulacion_activa = True

# TODO PARA EL ESTUDIANTE:
# 1. Define los mecanismos de sincronización necesarios:
# - Un cerrojo (Lock) o semáforo binario para exclusión mutua en el tarro.
# - Un semáforo para despertar al oso cuando el tarro esté lleno.
# - Un semáforo para que las abejas esperen si el tarro está lleno o el oso está comiendo.
mutex = threading.Lock()
sem_oso = threading.Semaphore(0)
sem_tarro_disponible = threading.Semaphore(1)

def abeja(id_abeja):
    global tarro_miel, simulacion_activa
    while simulacion_activa:
        time.sleep(random.uniform(0.05, 0.2))
        
        # TODO: Sincronizar el acceso al tarro de miel:
        # 1. Esperar a que el tarro esté disponible.
        sem_tarro_disponible.acquire()

        if not simulacion_activa:
            sem_tarro_disponible.release()
            break
        
        # 2. Entrar en exclusión mutua con el tarro.
        # 3. Depositar una porción de miel (tarro_miel += 1).
        with mutex:
            tarro_miel += 1
            lleno = (tarro_miel == M)
            print(f"🐝 Abeja {id_abeja} deposita miel -> tarro = {tarro_miel}/{M}")
 
        if lleno:
            # 4. Si tarro_miel == M, avisar/despertar al oso dormido.
            print(f"🐝 Abeja {id_abeja} llenó el tarro y despierta al oso")
            sem_oso.release()

        else:
            # 5. No está lleno: otras abejas pueden seguir depositando.
            sem_tarro_disponible.release()

def oso(max_tarros=2):
    global tarro_miel, simulacion_activa
    tarros_comidos = 0
    while tarros_comidos < max_tarros and simulacion_activa:
        # =====================================================================
        # TODO PARA EL ESTUDIANTE:
        # 1. Esperar pasivamente (bloqueado) hasta que una abeja señale que el tarro está lleno:
        sem_oso.acquire()
        
        # 2. Comerse toda la miel (tarro_miel = 0).
        with mutex:
            print(f"Oso despierta y se come {tarro_miel} porciones")
            tarro_miel = 0

        # 3. Incrementar tarros_comidos += 1.
        tarros_comidos += 1
        time.sleep(0.1)                            # digiriendo
        print(f"Oso termina el tarro {tarros_comidos}/{max_tarros} y vuelve a dormir")
 
        # Si fue el último tarro, se marca el fin ANTES de liberar a las abejas,
        # para que ninguna vuelva a depositar.
        if tarros_comidos == max_tarros:
            simulacion_activa = False

        # 4. Avisar a las abejas que el tarro está vacío y disponible (sem_tarro_disponible.release()).
        # =====================================================================
        sem_tarro_disponible.release()
        
    simulacion_activa = False

if __name__ == "__main__":
    print("=" * 60)
    print(" Iniciando Simulación: El Oso y las Abejas (UNJu FI)")
    print("=" * 60)
    
    hilo_oso = threading.Thread(target=oso, args=(2,), name="Oso")
    hilos_abejas = [
        threading.Thread(target=abeja, args=(i + 1,), name=f"Abeja-{i + 1}")
        for i in range(NUM_ABEJAS)
    ]
 
    hilo_oso.start()
    for h in hilos_abejas:
        h.start()
 
    hilo_oso.join()
    for h in hilos_abejas:
        h.join()
 
    print("=" * 60)
    print(f" Simulación finalizada. Miel restante en el tarro: {tarro_miel}")
    print("=" * 60)

