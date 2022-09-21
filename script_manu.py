import hashlib
import sys
import os
import logging

# CONSTANTES GLOBALES
BLOCK_SIZE = 65536 # tamanyo de cada bloque del archivo
FILE = "./README.md"
TEXTO = """Este script comprobara diariamente que los datos siguen siendo legitimos, usted podra hacer uso de este con el algoritmo sha256 y el algoritmo sha1 de la siguiente manera
script.py sha256
script.py sha1"""

# VARIABLES

hashes = dict() # Diccionario con el hash calculado la primera vez
new_hash = dict() # Diccionario con el hash calculado ahora mismo para compararlo con el antiguo
CONTADOR = 0


logging.basicConfig(filename='log.log', encoding='utf-8', level=logging.DEBUG)

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

    with open(archivo,'rb') as f:
        fb = f.read(bs)
        
        while len(fb) > 0:
            fb = f.read(bs)
            h.update(fb)

    return h.hexdigest()


# Calculamos el hash de todos los archivos en el directorio dado
# recibe alg(sha256 o sha1) - directorio(sobre el que se haran los hashes de los archivos) - dict(el diccionario de los hashes antiguos o el nuevo)
def hash_todo_directorio(alg,directorio,dict):
    
    nombres = os.listdir(directorio) # Nombre de todos los archivos en el directorio dado
    archivos = [os.path.join(directorio, nombre) for nombre in nombres] # Ruta completa de cada archivo en el directorio
    
    for x in archivos: # HORRIBLE. LO ARREGLARE
       match alg:
        case 'sha1':
            dict[x] = alg_sha1(x)
        case 'sha256':
            dict[x] = alg_sha256(x)

    guardar_hash("hash", dict)


# Guardar los hashes calculados junto con el nombre de los archivos en el fichero
def guardar_hash(file,dict):

    pfile = open(file,"w")
    for key,value in dict.items():
        pfile.write(key + ":" + value)
        pfile.write("\n")


# Comparador de hashes
def comp_hash(alg,directorio):

    contador = 0

    hash_todo_directorio(alg,directorio,new_hash)

    for archivo,hash in hashes.items():
        if archivo in new_hash:
            if hash == new_hash[archivo]:
                pass
            else:
                contador+=1
                logging.warning('El archivo ' + archivo + ' ha sido MODIFICADO')
    # print(contador)

    return contador


# Actualizamos el diccionario con los hashes
def actualizar_dict_hash():

    file = open("hash","r")
    for linea in file:

        ruta,resto = os.path.split(linea) # Te devuelve la ruta y el resto
        fichero = resto.split(':')[0]
        hash = resto.split(':')[1]

        hashes[ruta+"\\"+fichero] = hash.split('\n')[0]



def main():

    print('Ejecutando el script')

    args = sys.argv # guardamos los argumentos que pasamos en el script y comprobamos que algoritmo utilizara
    actualizar_dict_hash()
    
    if(len(args)>1):

        tipo_alg = args[1] # args es ['.\\script_manu.py', 'sha1']

        match tipo_alg:
            case 'sha256': # Si ejecutamos: script.py sha256
                print("Hay cambios en ", comp_hash('sha256', r'C:\Users\Manuel\Documents\SSII-code\SSII-PAI1\archivos'), " archivos.")
            

            case 'sha1': # Si ejecutamos: script.py sha1
                print("Hay cambios en ", comp_hash('sha1',r'C:\Users\Manuel\Documents\SSII-code\SSII-PAI1\archivos'), " archivos.")
    
    print('Script finalizado')

    return TEXTO


if __name__ == "__main__":
    main()
