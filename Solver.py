from Trelica import Trelica
import sympy as sp
import numpy as np
from math import sin, cos, pi, tan, sqrt, copysign


class Solver:
    """
    Essa classe Resolve uma treliça sujeita a cargas externas constantes,
    determinando os deslocamentos de seus nós e os esforços internos de seus elementos.
    Isso é feito pela biblioteca Sympy, que serve para  resolução computacional de
    problemas matemáticos que envolvem símbolos (sistemas lineares, nesse caso).
    """

    def __init__(self, trelica):

        self.trelica = trelica
        self.nodes = trelica.nodes
        self.size = 2 * len(self.trelica.nodes)
        self.K = trelica.getKMatrix()
        self.F = np.zeros(self.size)

        self.uCondContorno = np.array([-1] * self.size).reshape(self.size, 1)  # vetor u incompleto
        self.apoiosCondContorno = [None] * self.size  # vetor f incompleto
        self.cargasExternas = trelica.cargasExternas
        self.forcasApoios = [None] * self.size
        self.forcasExternas = [None] * self.size
        self.X = sp.zeros(self.size, 1)
        # atributo utilizado unicamente para determinar as forças internas
        shape = (len(self.trelica.elements), 2)
        self.vetorFint = np.zeros(shape)

    def setCondicoesContorno(self):
        """
        Essa função estabelece as condições de contorno para cada nó, considerando seu tipo.
        """
        n = self.size
        self.apoiosCondContorno = sp.Matrix([sp.symbols('R{}'.format(j + 1)) for j in range(n)])
        for node in self.nodes:
            key = node.key
            if node.type == 'apoio_fixo':
                self.uCondContorno[2 * key - 2] = 0
                self.uCondContorno[2 * key - 1] = 0

            elif node.type == 'apoio_livre_horizontal':
                self.uCondContorno[2 * key - 2] = 0
                self.apoiosCondContorno[2 * key - 1] = 0
            elif node.type == 'apoio_livre_vertical':
                self.uCondContorno[2 * key - 1] = 0
                self.apoiosCondContorno[2 * key - 2] = 0

            elif node.type == 'no_comum':
                self.apoiosCondContorno[2 * key - 2] = 0
                self.apoiosCondContorno[2 * key - 1] = 0

        for i in range(self.size):
            if self.uCondContorno[i] is None:
                self.uCondContorno[i] = -1

        self.uCondContorno = sp.Matrix(self.uCondContorno)
        for i in range(self.size):
            expr = self.uCondContorno[i]
            if expr.evalf() == -1:
                self.uCondContorno[i] = sp.symbols('q{}'.format(i + 1))

    def setForcasExternas(self):
        """
        Essa função constrói a matriz de forças externas (F).
        Aqui, somamos as reações de apoio e as cargas.
        :return:
        """
        cargasExternas = sp.Matrix(self.cargasExternas)
        self.F = cargasExternas + self.apoiosCondContorno

    def calcularQeF(self):
        """
        Resolve o sistema Ku - f = 0 por meio da bibliteca sympy.
        :return: Dicionários com os valores de deslocamentos e reações de apoio (nós comuns que não são apoios terão valor zero para essa força,
        como é esperado).
        """
        self.setCondicoesContorno()
        self.setForcasExternas()
        K_sp = sp.Matrix(self.K)
        self.X = self.F - K_sp * self.uCondContorno

        #escolhendo os simbolos de maneira generalizada
        simbolos = []
        for i in range(self.size):
            q = sp.symbols('q{}'.format(i + 1))
            R = sp.symbols('R{}'.format(i + 1))
            simbolos.append(q)
            simbolos.append(R)

        solution = sp.solve(self.X, simbolos)
        solution = {str(key): value for key, value in solution.items()}

        self.F = np.zeros(self.size)
        for i in range(self.size):
            if f'R{i + 1}' in solution:
                self.F[i] = round(solution[f'R{i + 1}'], 2)

        self.q = np.zeros(self.size)

        for j in range(self.size):
            if f'q{j + 1}' in solution:
                self.q[j] = solution[f'q{j + 1}']

        dictF = {f'R{i + 1}': round(self.F[i],2) for i in range(len(self.F))}
        dictQ = {f'q{i + 1}': round(self.q[i],5) for i in range(len(self.q))}

        return dictF, dictQ

    def calcularForcasInternas(self):
        """
        Calcula as reações internas em cada barra a partir das reações de apoio determinadas.
        :return: Dicionário com os valores das forças internas.
        """
        _, dictQ = self.calcularQeF()

        qValues = list(dictQ.values())

        for element in self.trelica.elements:
            A, B = element.A, element.B
            # calculando vetorialmente a diferença entre os comprimentos
            dx = qValues[2 * B.getKey() - 2] - qValues[2 * A.getKey() - 2]
            dy = qValues[2 * B.getKey() - 1] - qValues[2 * A.getKey() - 1]

            u = np.array([element.x, element.y])
            v = np.array([element.x + dx, element.y + dy])

            dL = np.linalg.norm(v) - np.linalg.norm(u)

            F = element.EA * dL / element.L

            element.Fint = F   # estabelecendo o sinal da força: se comprimir em y, é negativa

        forcasInternas = {f'F_{i+1}': round(self.trelica.elements[i].Fint, 2) for i in
                          range(len(self.trelica.elements))}

        return forcasInternas

    def solve(self):
        """
        Retorna todos os parâmetros que queremos determinar
        :return: Vetor de Reações de Apoio, deslocamento em cada barra e força interna em cada barra.
        """
        F, q = self.calcularQeF()
        Fint = self.calcularForcasInternas()

        return F, q, Fint
