from email.encoders import encode_noop
from genericpath import isfile
import hashlib
import sys
import os
import logging
import schedule
import time
from configparser import ConfigParser

# CONSTANTES GLOBALES
BLOCK_SIZE = 65536 # tamanyo de cada bloque del archivo


# VARIABLES
hashes = dict() # Diccionario con el hash calculado la primera vez
new_hash = dict() # Diccionario con el hash calculado ahora mismo para compararlo con el antiguo
CONTADOR = 0
INCIDENTES_MES = dict()

# Extraer configuraciones
configParser = ConfigParser() #Creamos el objeto para leer el conf
configParser.read(r'directorios.conf') #especificamos el archivo a leer
timeInterval = configParser.get('CONFIG', 'Tiempo') #Extraemos el intervalo de tiempo
directorios = configParser.get('CONFIG', 'Directorios').strip("[]").split(",") #Se convierte el String a un Array de direcciones

# logging.basicConfig(filename='log.log', encoding='utf-8')

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


# Calculamos el hash de todos los archivos en el directorio dado
# recibe alg(sha256 o sha1) - directorio(sobre el que se haran los hashes de los archivos) - dict(el diccionario de los hashes antiguos o el nuevo)
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


# Guardar los hashes calculados junto con el nombre de los archivos en el fichero
def guardar_hash(file,dict):

    pfile = open(file,"w")
    for key,value in dict.items():
        pfile.write(key + ":" + value)
        pfile.write("\n")


# Comparador de hashes
def comp_hash(alg,directorios):

    contador = 0
    infectado = []

    for directorio in directorios:
        hash_todo_directorio(alg,directorio,new_hash)

        for archivo,hash in hashes.items():
            if archivo in new_hash:
                if hash == new_hash[archivo] or (archivo in infectado):
                    pass
                else:
                    contador+=1
                    daily_log.warning('El archivo ' + archivo + ' ha sido MODIFICADO. Hora: {}'.format(time.asctime()))
                    infectado.append(archivo)
                    if archivo not in INCIDENTES_MES: 
                        INCIDENTES_MES[archivo] = format(time.asctime())
        if contador==0:
            daily_log.warning('Ningún archivo ha sido modificado. Hora: {}'.format(time.asctime()))

    return contador


# Actualizamos el diccionario con los hashes
def actualizar_dict_hash(tipo_alg):
    # Correr el primer Analisis:
    comp_hash(tipo_alg, directorios)

    file = open("hash","r")
    for linea in file:
        ruta,resto = os.path.split(linea) # Te devuelve la ruta y el resto
        fichero = resto.split(':')[0]
        hash = resto.split(':')[1]
        hashes[ruta+"\\"+fichero] = hash.split('\n')[0]
        

def monthly_report():
    
    print('Se ejecuta monthly report')
    dia_mes = int(time.strftime('%d')) # strftime devuelve str. Convertir a int
    print('dia_mes = ', dia_mes)
    if dia_mes != 29:
        # No es primero de mes
        return
    else:
        print('SE TIENE QUE EJECUTAR REPORT')
        monthly_log.critical('Reporte del mes {}: Número de incidentes: {}'.format(time.strftime('%m/%y'), len(INCIDENTES_MES)))
        
        if len(INCIDENTES_MES) > 0:
            for error in INCIDENTES_MES:
                monthly_log.warning(f'El archivo "{error}" fue modificado el {INCIDENTES_MES[error]}')

        monthly_log.critical('----- Fin del reporte del mes -----')
        INCIDENTES_MES.clear()
        # monthly_log.warning('Reporte del mes {}: Número de incidentes: {}'.format(time.strftime('%m'), INCIDENTES_MES))



def setup_logger(name, log_file):

    print('Se ejecuta setup_logger')

    handler = logging.FileHandler(log_file, encoding='utf-8')
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.WARNING)
    logger.addHandler(handler)

    return logger

daily_log = setup_logger('daily_log', 'log.log')
monthly_log = setup_logger('monthly_log', 'mensual.log')

def main():

    print('Ejecutando el script')

    args = sys.argv # guardamos los argumentos que pasamos en el script y comprobamos que algoritmo utilizara
    if(len(args)>1):
        tipo_alg = args[1] # args es ['.\\script_manu.py', 'sha1']
        actualizar_dict_hash(tipo_alg)
        
        schedule.every(5).seconds.do(run_analysis,tipo_alg)
        #schedule.every().day.at(timeInterval).do(run_analysis, tipo_alg)
        schedule.every().day.at(timeInterval).do(monthly_report)
        
        while True:
            schedule.run_pending()
            time.sleep(1)
    else: 
        print('Script Finalizado - Falta un Argumento')

def run_analysis(tipo_alg):
    time_inicio = time.time() 
    print("Corre Analisis")
    
    match tipo_alg:
            case 'sha256': # Si ejecutamos: script.py sha256
                print("Hay cambios en ", comp_hash('sha256', directorios), " archivos.")


            case 'sha1': # Si ejecutamos: script.py sha1
                print("Hay cambios en ", comp_hash('sha1', directorios), " archivos.")
    print("Termina Analisis") 
    print(time.time()-time_inicio," Segundos")

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
    hash_todo_directorio('sha256','C:\\Users\\Puche\\Documents\\GitHub\\SSII-PAI1\\archivos\\archivos2',hashes)
    proof_of_possesion('C:\\Users\\Puche\\Documents\\GitHub\\SSII-PAI1\\archivos\\archivos2\\fantasma.jpg7d75b')
    hashes = dict()

    main()
