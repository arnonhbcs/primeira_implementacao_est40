import numpy as np
import sympy as sp
class Node:
    """
    Essa classe representa os nós de uma treliça.
    Seus atributos são as coordenadas do nó no plano
    (um deles será escolhido como origem, normalmente
    o nó 1), o número atribuído ao nó pelo problema e
    o tipo do nó (apoio fixo, apoio livre, nó comum etc)
    """
    def __init__(self, x, y, key: int, tipo='no_comum'):
        self.x = x
        self.y = y
        self.key = key
        self.type = tipo
        # atributos usados apenas para calcular forças internas
        self.qx = 0
        self.qy = 0

    def getKey(self):
        return self.key


