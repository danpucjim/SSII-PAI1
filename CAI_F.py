from ast import Lambda
from email.encoders import encode_noop
from genericpath import isfile
import hashlib
import sys
import os
import logging
from typing import Dict
import schedule
import time
from configparser import ConfigParser

"""
FUNCIONES
"""
BLOCK_SIZE = 65536 # tamanyo de cada bloque del archivo
fichero_root1 = 'C:\Users\mendo\Desktop\Proyectos\US_ES_SSII\SSII-PAI1\fichero1'
fichero_root2 = 'C:\Users\mendo\Desktop\Proyectos\US_ES_SSII\SSII-PAI1\fichero2'
main_tree1 = dict()
main_tree2 = dict()

class Node:
  def __init__(self, ruta, isRoot=False):
    self.hash = None
    self.left = None
    self.right = None
    self.ruta = ruta
    self.isRoot = isRoot

# Algoritmo de hash para sha256
def alg_sha256(file):
    h = hashlib.sha256() # Crear el objeto hash
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


def crear_arbol(route, tree, fatherNode=None):

    nombres = os.listdir(route) # Nombre de todos los archivos en el directorio dado
    archivos = [os.path.join(route, nombre) for nombre in nombres] # Ruta completa de cada archivo en el directorio
    
    localcount = 0
    for x in archivos: # HORRIBLE. LO ARREGLARE

        newNode = Node(archivos)
        tree[hash] = newNode

        if os.path.isfile(x):
            # Si es un archivo
            hash = alg_sha256(x)
            newNode.hash = hash
        else:
            # Si es un directorio, hacer recursivamente a todos los archivos del directorio
            crear_arbol(x,tree, newNode)

def main():
    crear_arbol(fichero_root1, main_tree1)
    crear_arbol(fichero_root2, main_tree2)
    pass



if __name__ == "__main__":

    #PRUEBA DEL PROOF OF POSSESION
    #hash_todo_directorio('sha256','C:\\Users\\Puche\\Documents\\GitHub\\SSII-PAI1\\archivos\\archivos2',hashes)
    #proof_of_possesion('C:\\Users\\Puche\\Documents\\GitHub\\SSII-PAI1\\archivos\\archivos2\\fantasma.jpg7d75b')

    main()
