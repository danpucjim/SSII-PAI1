import hashlib
import sys
import os
import logging
import schedule
import time
from configparser import ConfigParser
import matplotlib.pyplot as plt

"""
CONSTANTES GLOBALES
"""
BLOCK_SIZE = 65536 # tamaño de cada bloque del archivo


"""
VARIABLES
"""
hashes = dict() # Diccionario con el hash calculado la primera vez
new_hash = dict() # Diccionario con el hash calculado ahora mismo para compararlo con el antiguo
CONTADOR = 0
INCIDENTES_MES = dict()


""""
EXTRAER CONFIGURACIONES
"""
configParser = ConfigParser() # Creamos el objeto para leer el conf
configParser.read(r'directorios.conf') # Especificamos el archivo a leer
timeInterval = configParser.get('CONFIG', 'Tiempo') # Extraemos el intervalo de tiempo
directorios = configParser.get('CONFIG', 'Directorios').strip("[]").split(",") # Se convierte el String a un Array de direcciones


"""
FUNCIONES
"""

# Algoritmo de hash para sha256
def alg_sha256(file):
    h = hashlib.sha256() # Crear el objeto hash
    return lect_archivo(file, BLOCK_SIZE, h)


# Algoritmo de hash para sha1
def alg_sha1(file):
    h = hashlib.sha1() # Crear el objeto hash
    return lect_archivo(file, BLOCK_SIZE, h)
    

# Lectura del archivo
def lect_archivo(archivo, bs, h):

    """ Algunos archivos pueden ser muy grandes.
        Partimos el archivo en varios trozos para que 
        quepen en memoria y asi sea mas eficiente. 
    """

    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(archivo, 'rb', buffering=0) as f:
        
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()



"""
Calculamos el hash de todos los archivos en el directorio dado.
 - alg: Tipo de algoritmo de hash a utilizar, sha256 o sha1
 - directorio: Directorio sobre el que se harán los hashes de los archivos
 - dict: Diccionario sobre el que se guardarán los hashes. Puede ser el antiguo o nuevo
"""

def hash_todo_directorio(alg,directorio,dict):
    
    nombres = os.listdir(directorio) # Nombre de todos los archivos en el directorio dado
    archivos = [os.path.join(directorio, nombre) for nombre in nombres] # Ruta completa de cada archivo en el directorio
    
    for x in archivos: # HORRIBLE. LO ARREGLARE

        if os.path.isfile(x):
            # Si es un archivo
            match alg:
                case 'sha1':
                    dict[x] = alg_sha1(x)
                case 'sha256':
                    dict[x] = alg_sha256(x)
        else:
            # Si es un directorio, hacer recursivamente a todos los archivos del directorio
            hash_todo_directorio(alg,x,dict)

    guardar_hash("hash", dict)



"""
Función que guarda los hashes calculados junto con el nombre de los archivos
en el fichero correspondiente.
 - file: Archivo donde guardaremos los hashes
 - dict: Diccionario que contiene los hashes que queremos guardar
"""

def guardar_hash(file,dict):

    pfile = open(file,"w")
    for key,value in dict.items():
        pfile.write(key + ":" + value)
        pfile.write("\n")


"""
Función que compara los hashes de los archivos. Si detecta cambios, lo notifica en el log.
"""
def comp_hash(alg,directorios):

    contador = 0
    infectado = []

    for directorio in directorios:
        hash_todo_directorio(alg,directorio,new_hash)

        for archivo,hash in hashes.items():
            if archivo in new_hash:
                if hash == new_hash[archivo] or (archivo in infectado):
                    # No hay cambios.
                    pass
                else:
                    contador+=1
                    daily_log.warning(f'El archivo {archivo} ha sido MODIFICADO. Hora: {time.asctime()}')
                    infectado.append(archivo)
                    
                    if archivo not in INCIDENTES_MES: 
                        INCIDENTES_MES[archivo] = format(time.asctime())
        if contador==0:
            daily_log.warning(f'Ningún archivo ha sido modificado. Hora: {time.asctime()}')

    return contador


"""
Actualizamos el diccionario con los hashes.
"""
def actualizar_dict_hash(tipo_alg):
    
    # Realizar el primer análisis:
    comp_hash(tipo_alg, directorios)

    file = open("hash","r")
    for linea in file:
        ruta,resto = os.path.split(linea) # Te devuelve la ruta y el resto
        fichero = resto.split(':')[0]
        hash = resto.split(':')[1]
        hashes[ruta+"\\"+fichero] = hash.split('\n')[0]


"""
Función que genera el informe mensual que se guarda en el archivo mensual.log
"""
def monthly_report():
    
    print('Se ejecuta monthly report')
    
    dia_mes = int(time.strftime('%d')) # strftime devuelve str. Convertir a int
    if dia_mes != 2:
        # NO se ejecuta. No es primero de mes
        return
    else:
        monthly_log.critical('Reporte del mes {}: Número de incidentes: {}'.format(time.strftime('%m/%y'), len(INCIDENTES_MES)))
        
        if len(INCIDENTES_MES) > 0:
            for error in INCIDENTES_MES:
                monthly_log.warning(f'El archivo "{error}" fue modificado el {INCIDENTES_MES[error]}')

        generar_grafica(time.strftime('%m'))
        
        monthly_log.critical('----- Fin del reporte del mes -----')
        INCIDENTES_MES.clear() # Vaciar el diccionario para poder utilizarlo en el siguiente reporte mensual.


"""
Función que sirve para configurar los diferentes logs que utilizamos (log diario y log mensual).
 - name: Nombre del log
 - log_file: Nombre del archivo que corresponde al log
"""
def setup_logger(name, log_file):

    handler = logging.FileHandler(log_file, encoding='utf-8')
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.WARNING)
    logger.addHandler(handler)

    return logger

daily_log = setup_logger('daily_log', 'log.log')
monthly_log = setup_logger('monthly_log', 'mensual.log')


"""
Función que genera la gráfica correspondientes al reporte mensual
"""
def generar_grafica(mes):

    print('E----- Ejecutando generador de gráfica mensual -----')

    # Reportes mensuales
    labels = ["infectados", "no infectados"]

    # Calculamos los archivos totales en el directorio y subdirectorios
    num_archivos = 0
    for directorio in directorios:

        for _,_, files in os.walk(directorio): # Devuelve 3 parámetros. Solo queremos saber los archivos
            num_archivos+= len(files)

    num_infectados = len(INCIDENTES_MES)
    y = [num_infectados/num_archivos, (num_archivos-num_infectados)/num_archivos] # En porcentajes

    plt.pie(y, labels=labels, autopct='%1.1f%%')
    plt.legend()
    plt.title(f'Reporte mensual del mes {mes}')
    plt.savefig(f'reporte_mensual_{mes}.png')



def main():

    print('----- Ejecutamos el script -----')

    args = sys.argv # Guardamos los argumentos que pasamos en el script y comprobamos que algoritmo utilizara
    
    if(len(args)>1):
        tipo_alg = args[1] # Valores que devuelve args, nombre del archivo y tipo de alg: ['.\\script_manu.py', 'sha1']
        
        actualizar_dict_hash(tipo_alg)
        
        schedule.every(5).seconds.do(run_analysis,tipo_alg)
        schedule.every().day.at(timeInterval).do(monthly_report)
        
        while True:
            schedule.run_pending()
            time.sleep(1)
    else: 
        print('Script finalizado - Falta un argumento')


def run_analysis(tipo_alg):
    
    time_inicio = time.time() 
    print("Corre Analisis")
    
    match tipo_alg:
            case 'sha256': # Si ejecutamos: script.py sha256
                print("Hay cambios en ", comp_hash('sha256', directorios), " archivos.")


            case 'sha1': # Si ejecutamos: script.py sha1
                print("Hay cambios en ", comp_hash('sha1', directorios), " archivos.")
    # print("Termina Analisis") 
    # print(time.time()-time_inicio," Segundos")


def proof_of_possesion(mensaje):
    """
    Parametro -> mensaje estilo rutanumero
    La funcion parte este mensaje en dos para acceder a la ruta dada y comprobar si los ultimos 5 digitos coinciden con los que tiene el servidor
    """
    ruta = mensaje[0:-5]
    numero = mensaje[-5:]

    if(hashes[ruta][-5:] == numero):
        print("Token de acceso")


if __name__ == "__main__":

    #PRUEBA DEL PROOF OF POSSESION
    # hash_todo_directorio('sha256','C:\\Users\\Puche\\Documents\\GitHub\\SSII-PAI1\\archivos\\archivos2',hashes)
    # proof_of_possesion('C:\\Users\\Puche\\Documents\\GitHub\\SSII-PAI1\\archivos\\archivos2\\fantasma.jpg7d75b')
    # hashes = dict()

    main()
