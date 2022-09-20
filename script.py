import base64
import hashlib
import sys

# CONSTANTES GLOBALES
BLOCK_SIZE = 65536 # tamanyo de cada bloque del archivo
FILE = "./README.md"
TEXTO = """Este script comprobara diariamente que los datos siguen siendo legitimos, usted podra hacer uso de este con el algoritmo sha256 y el algoritmo sha1 de la siguiente manera
script.py sha256
script.py sha1"""

#FUNCIONES

def main():
    args = sys.argv # guardamos los argumentos que pasamos en el script y comprobamos que algoritmo utilizara
    
    if(len(args)>1):
        #si ejecutamos el script.py sha256
        if(args[1] == 'sha256'):
            print(alg_sha256())
            return args
        # si ejecutamos el script.py sha1
        elif(args[1] == 'sha1'):
            print(alg_sha1())
            return args

    return TEXTO
    
#algoritmo de hash para sha256
def alg_sha256():
    h = hashlib.sha256()
    return lect_arch(FILE,BLOCK_SIZE,h)

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


#-----------------------------------------------------------------------------------------------------#
main()