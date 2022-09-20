import base64
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

hashes = dict() #directorio con el hash calculado la primera vez
new_hash = dict() # directorio con el hash calculado ahora mismo para compararlo con el antiguo

#FUNCIONES

def main():
    args = sys.argv # guardamos los argumentos que pasamos en el script y comprobamos que algoritmo utilizara

    if(len(args)>1):
        #si ejecutamos el script.py sha256
        if(args[1] == 'sha256'):
            all_directories('sha256','.',hashes)
            comp_hash('sha256','.')
            return args
        # si ejecutamos el script.py sha1
        elif(args[1] == 'sha1'):
            all_directories('sha1','.',hashes)
            return args

    return TEXTO
    
#algoritmo de hash para sha256
def alg_sha256(file):
    h = hashlib.sha256()
    return lect_arch(file,BLOCK_SIZE,h)

#algoritmo de hash para sha1
def alg_sha1():
    h = hashlib.sha1()
    return lect_arch(FILE,BLOCK_SIZE,h)
    

# lee el archivo que queremos hashear
def lect_arch(archivo,bs,h):
    with open(archivo,'rb')as f:
        fb = f.read(bs)
        while len(fb) > 0:
            h.update(fb)
            fb = f.read(bs)
    return h.hexdigest()

# va haciendo el hash de todos los archivos dado un directorio dado
# recibe alg(sha256 o sha1) - directorio(sobre el que se haran los hashes de los archivos) - dict(el diccionario de los hashes antiguos o el nuevo)
def all_directories(alg,directorio,dict):
    directorios = os.listdir()
    for directorio in directorios:
        #ESTO TENGO QUE CAMBIARLO!!
        if(directorio=='.git'):
            print("NO ACCESO")
        else:
            dict[directorio] = alg_sha256(directorio)
            guardar_hash("hash",dict)
    print(hashes)

# guarda el directorio : hash en el archivo hash para compararlo cada dia al recalcular los hashes
def guardar_hash(file,dict):
    pfile = open(file,"w")
    for key,value in dict.items():
        pfile.write(key + ":" + value)
        pfile.write("\n")

#Comparador de hashes(hay que terminarlo)

def comp_hash(alg,directorio):
    all_directories(alg,directorio,new_hash)
    print("ESTES",new_hash)

#-----------------------------------------------------------------------------------------------------#
main()
