from random import Random 
import binarytree, copy, time

"""
FUNCIONES
"""

def main():  
    tree1 = binarytree.tree(height=3, is_perfect=True)
    tree2 = copy.copy(tree1)

    random = Random()
    changeRandomIndex = random.randint(0, (2**(tree1.height+1))-2)
    print('ToChange', changeRandomIndex)

    print('------Tree1------',tree1)

    tree2[changeRandomIndex].value = random.randint(0, (2**(tree1.height+1))-2)
    print('------Tree2------',tree2)
    
    # time.sleep(1)
    print(compare_hashes(tree1, tree2))
    

def compare_hashes(tree1, tree2):
    if (tree1.height != tree2.height):
        return "Error: Los arboles no son iguales"
    
    getLastIndex = (2**(tree1.height+1))-1
    allIndexes = list(range(0, getLastIndex))

    for index in allIndexes:
        print(f'Index: {index} Values: {tree1[index].value} -- {tree2[index].value}')
        if not(tree1[index].value == tree2[index].value):
            print('error')
            return f'Error: Se encontró una diferencia en el Indice: {index}'
    else:
        return "Los arboles son correctos"
    

if __name__ == "__main__":

    #PRUEBA DEL PROOF OF POSSESION
    #hash_todo_directorio('sha256','C:\\Users\\Puche\\Documents\\GitHub\\SSII-PAI1\\archivos\\archivos2',hashes)
    #proof_of_possesion('C:\\Users\\Puche\\Documents\\GitHub\\SSII-PAI1\\archivos\\archivos2\\fantasma.jpg7d75b')

    main()
