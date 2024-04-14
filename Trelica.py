from Element import Element
from Node import Node
from typing import List
import numpy as np


class Trelica:
    """
    Essa classe representa uma Treliça sujeita a cargas externas constantes. Para utilizá-la,
    definimos quais são os elementos estruturais, as cargas externas às quais esses elementos estão sujeitos
    e as condições de contorno, obtendo a matriz de rigidez da estrutura global.
    """
    def __init__(self, nodes: List[Node]):
        self.nodes = nodes
        self.size = 2 * len(nodes)
        self.elements: List[Element] = []
        self.K = np.zeros((self.size, self.size))
        self.cargasExternas = np.zeros((self.size, 1))
        self.condicoesContorno = []

    def getKMatrix(self):
        return self.K

    def setKMatrix(self, K):
        self.K = K
    def computeElement(self, aKey: int, bKey: int, key: int):
        """
        Essa função insere na representação da treliça uma barra entre dois nós.
        :param aKey: o índice do primeiro nó do elemento.
        :param bKey: o índice do segundo nó do elemento.
        """
        aX, aY, bX, bY = -1, -1, -1, -1

        if aKey > self.size or bKey > self.size:
            print('ERRO: NÓ INVÁLIDO')

        else:
            for node in self.nodes:
                if node.key == aKey:
                    aX, aY, aType = node.x, node.y, node.type
                elif node.key == bKey:
                    bX, bY, bType = node.x, node.y, node.type

            el = Element(
                Node(aX, aY, aKey, aType),
                Node(bX, bY, bKey, bType),
                key
            )
            el.computeKMatrix()

            self.elements.append(el)
            self.computeKMatrix()

    def computeKMatrix(self):
        """
        Calcula a Matriz de Rigidez da Estrutura Global(treliça)
        a partir das matrizes de rigidez de cada elemento.
        """
        self.setKMatrix(np.zeros((self.size, self.size)))
        for element in self.elements:
            A, B = element.getNodes()
            aKey, bKey = A.getKey(), B.getKey()
            elementK = element.getKMatrix()

            # submatrizes da matriz de rigidez do elemento
            Ka = elementK[0:2, 0:2]
            Kb = elementK[0:2, 2:]
            Kc = elementK[2:, 0:2]
            Kd = elementK[2:, 2:]

            # somar essas matrizes nos devidos lugares da matriz global
            self.K[2 * aKey - 2:2 * aKey, 2 * aKey - 2:2 * aKey] += Ka
            self.K[2 * aKey - 2:2 * aKey, 2 * bKey - 2:2 * bKey] += Kb
            self.K[2 * bKey - 2:2 * bKey, 2 * aKey - 2:2 * aKey] += Kc
            self.K[2 * bKey - 2:2 * bKey, 2 * bKey - 2:2 * bKey] += Kd

    def computeCargasExternas(self, nodeKey: int, forceVector: List[float]):
        """
        Computa as cargas externas às quais a treliça está sujeita
        :param nodeKey: Nó que sofre ação da carga externa.
        :param forceVector: vetor bidimensional representando os valores das cargas
        no nó.
        :return: sem retorno.
        """
        for node in self.nodes:
            if node.key == nodeKey:
                self.cargasExternas[2*nodeKey-2, 0] = forceVector[0]
                self.cargasExternas[2 * nodeKey - 1, 0] = forceVector[1]

    def getCargasExternas(self):
        return self.cargasExternas















