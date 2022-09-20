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
CONTADOR = 0

#FUNCIONES
    
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
            pass
        else:
            dict[directorio] = alg_sha256(directorio)

# guarda el directorio : hash en el archivo hash para compararlo cada dia al recalcular los hashes
def guardar_hash(file,dict):
    pfile = open(file,"w")
    for key,value in dict.items():
        pfile.write(key + ":" + value)
        pfile.write("\n")

#Comparador de hashes(hay que terminarlo)
def comp_hash(alg,directorio):
    contador = 0
    all_directories(alg,directorio,new_hash)
    for keys,values in hashes.items():
        if hashes[keys] == new_hash[keys]:
            pass
        else:
            contador+=1
    print(contador)
    return contador

#guardamos los datos del archivo hash en la variable hashes
def recuperar_hash():
    file = open("hash","r")
    print(file)
    for linea in file:
        datos = linea.split(":")
        hashes[datos[0]] = datos[1].split('\n')[0]


def main():
    args = sys.argv # guardamos los argumentos que pasamos en el script y comprobamos que algoritmo utilizara
    recuperar_hash()
    if(len(args)>1):
        #si ejecutamos el script.py sha256
        if(args[1] == 'sha256'):
            print("Hay cambio en",comp_hash('sha256','.'),"archivos posible infeccion")
            return args
        # si ejecutamos el script.py sha1
        elif(args[1] == 'sha1'):
            all_directories('sha1','.',hashes)
            return args

    return TEXTO

#-----------------------------------------------------------------------------------------------------#
main()
