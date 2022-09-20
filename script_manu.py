import hashlib
import sys
import os

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
    
    archivos = os.listdir(directorio) # Nombre de todos los archivos en el directorio dado
    
    for x in archivos: # HORRIBLE. LO ARREGLARE
        if(x==".git"):
            pass
        else:
            dict[x] = alg_sha256(x)


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
        if hash == new_hash[archivo]:
            pass
        else:
            contador+=1
    # print(contador)

    return contador


# Actualizamos el diccionario con los hashes
def actualizar_dict_hash():

    file = open("hash","r")
    print(file)
    for linea in file:
        datos = linea.split(":")
        hashes[datos[0]] = datos[1].split('\n')[0]



def main():

    print('Ejecutando el script')

    args = sys.argv # guardamos los argumentos que pasamos en el script y comprobamos que algoritmo utilizara
    
    actualizar_dict_hash()
    
    if(len(args)>1):

        match args:
            case 'sha256': # Si ejecutamos: script.py sha256
                print("Hay cambio en ", comp_hash('sha256',r'C:\Users\Manuel\Documents\SSII-code\SSII-PAI1\archivos'), " archivos.")
                return args
            
            case 'sha1': # Si ejecutamos: script.py sha1
                hash_todo_directorio('sha1','.',hashes)
                return args
    
    print('Script finalizado')

    return TEXTO


if __name__ == "__main__":
    main()
