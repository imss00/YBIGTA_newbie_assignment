from __future__ import annotations
import copy


"""
TODO:
- __setitem__ 구현하기
- __pow__ 구현하기 (__matmul__을 활용해봅시다)
- __repr__ 구현하기
"""


class Matrix:
    MOD = 1000

    def __init__(self, matrix: list[list[int]]) -> None:
        self.matrix = matrix

    @staticmethod
    def full(n: int, shape: tuple[int, int]) -> Matrix:
        return Matrix([[n] * shape[1] for _ in range(shape[0])])

    @staticmethod
    def zeros(shape: tuple[int, int]) -> Matrix:
        return Matrix.full(0, shape)

    @staticmethod
    def ones(shape: tuple[int, int]) -> Matrix:
        return Matrix.full(1, shape)

    @staticmethod
    def eye(n: int) -> Matrix:
        matrix = Matrix.zeros((n, n))
        for i in range(n):
            matrix[i, i] = 1
        return matrix

    @property
    def shape(self) -> tuple[int, int]:
        return (len(self.matrix), len(self.matrix[0]))

    def clone(self) -> Matrix:
        return Matrix(copy.deepcopy(self.matrix))

    def __getitem__(self, key: tuple[int, int]) -> int:
        return self.matrix[key[0]][key[1]]

    def __setitem__(self, key: tuple[int, int], value: int) -> None:
        """
        특정 위치에 값(mod(1000)으로 나눈 나머지)을 할당
        """
        self.matrix[key[0]][key[1]] = value % self.MOD

    def __matmul__(self, matrix: Matrix) -> Matrix:
        x, m = self.shape
        m1, y = matrix.shape
        assert m == m1

        result = self.zeros((x, y))

        for i in range(x):
            for j in range(y):
                for k in range(m):
                    result[i, j] += self[i, k] * matrix[k, j]

        return result

    def __pow__(self, n: int) -> Matrix:
        """
        행렬을 n번 제곱한 결과 반환
        """
        if n == 1:
            res = self.clone()
            for i in range(len(res.matrix)):
                for j in range(len(res.matrix[0])):
                    res.matrix[i][j] = res.matrix[i][j] % self.MOD
            return res
        
        half = self.__pow__(n // 2)

        result = half @ half

        if n % 2 == 1:
            result = result @ self
            
        return result

    def __repr__(self) -> str:
        """
        matrix를 문자로 출력 / 출력시 모양 지정
        """
        output = ""

        for i in range(len(self.matrix)):
            row_str = ""
            for j in range(len(self.matrix[i])):
                row_str += str(self.matrix[i][j]) + " "

            output += row_str.strip() + "\n"
        
        return output.strip()