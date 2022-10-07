from typing import List
import hashlib
import os

from CAI_F import lect_archivo


class Node:
    '''
    Clase nodo
    Atributos -> hijo izq, hijo derecho, valor, contenido, ha sido copiado , lista de archivos ya hasheados
    '''
    def __init__(self, left, right, value: str, ruta, is_copied=False) -> None:
        self.left: Node = left
        self.right: Node = right
        self.value = value
        self.ruta = ruta
        self.is_copied = is_copied
        self.archivos_hasheados = []

    @staticmethod
    def hash(val: str) -> str:
        return hashlib.sha1(val.encode()).hexdigest()
    
    def hash1(val:str) -> str:
        return lect_archivo(val,128*1024,hashlib.sha1())

    def __str__(self):
        return (str(self.value))

    def copy(self):
        """
        class copy function
        """
        return Node(self.left, self.right, self.value, self.ruta, True)


class MerkleTree:
    def __init__(self, values: List[str]) -> None:
        self.lista = []
        self.__buildTree(values)

    def __buildTree(self, values: List[str]) -> None:

        leaves: List[Node] = [Node(None, None, Node.hash1(e), e) for e in values]
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1].copy())  # duplicate last elem if odd number of elements
        self.root: Node = self.__buildTreeRec(leaves)

    def __buildTreeRec(self, nodes: List[Node]) -> Node:
        if len(nodes) % 2 == 1:
            nodes.append(nodes[-1].copy())  # duplicate last elem if odd number of elements
        half: int = len(nodes) // 2

        if len(nodes) == 2:
            nodo = Node(nodes[0], nodes[1], Node.hash(nodes[0].value + nodes[1].value), nodes[0].ruta+"+"+nodes[1].ruta)
            self.lista.append(nodo.value)
            self.lista.append(nodo.left.value)
            self.lista.append(nodo.right.value)
            return nodo

        left: Node = self.__buildTreeRec(nodes[:half])
        right: Node = self.__buildTreeRec(nodes[half:])
        valor_izq = Node.hash1(left.ruta)
        valor_der = Node.hash1(right.ruta)
        value: str = Node.hash(valor_izq + valor_izq)
        ruta: str = f'{left.ruta}+{right.ruta}'
        return Node(left, right, value, ruta)
        

    def printTree(self) -> None:
        self.__printTreeRec(self.root)

    def __printTreeRec(self, node: Node) -> None:
        if node != None:
            if node.left != None:
                print("Left: "+str(node.left))
                print("Right: "+str(node.right))
            else:
                print("Input")
                
            if node.is_copied:
                print('(Padding)')
            print("Value: "+str(node.value))
            print("Content: "+str(node.ruta))
            print("")
            self.__printTreeRec(node.left)
            self.__printTreeRec(node.right)

    def getRootHash(self) -> str:
        return self.root.value
    
    

def lect_archivo(archivo, bs, h):

        b  = bytearray(bs)
        mv = memoryview(b)
        with open(archivo, 'rb', buffering=0) as f:
        
            for n in iter(lambda : f.readinto(mv), 0):
                h.update(mv[:n])
        return h.hexdigest()

def hash_directorio(self,directorios):
    self.archivos_hasheados = []
    for n in directorios:
        print(lect_archivo(n,128*1024,hashlib.sha1()))
        self.archivos_hasheados.append(lect_archivo(n,128*1024,hashlib.sha1()))
    pass

def directorios(directorio):
        nombres = os.listdir(directorio)
        archivos = [os.path.join(directorio, nombre) for nombre in nombres]
        return archivos

def mixmerkletree(direct,direct1) -> None:
    
    elems = directorios(direct)
    elems1 = directorios(direct1)

    print("Inputs: ")
    print(*elems, sep=" | ")
    print("")

    mtree = MerkleTree(elems)
    mtree1 = MerkleTree(elems1)
    Hashes1 = mtree1.lista
    Hashes = mtree.lista
    mtree.printTree()
    mtree1.printTree()

    if(Hashes1[0]==Hashes[0]):
        print("No ha habido cambios")
    else:
        print("Ha habido cambios")
        for n in range(len(Hashes)):
            if(Hashes[n]!=Hashes1[n]):
                print("El cambio esta en el hash", Hashes[n],"----",Hashes1[n])
    


#print(lect_archivo("./fichero1/archivos2/texto.txt",128*1024,hashlib.sha1()))
#print(hashlib.sha1(b"./fichero1/archivos2\texto.txt").hexdigest())
mixmerkletree("./fichero1/archivos2","./fichero2/archivos2")