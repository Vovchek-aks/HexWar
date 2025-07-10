import numpy as np
import pygame as pg
from attrs import frozen, field


@frozen
class Matrix2:
    @classmethod
    def from_vectors(cls, vector1: pg.Vector2, vector2: pg.Vector2) -> "Matrix2":
        return cls(np.matrix([[vector1.x, vector1.y],
                              [vector2.x, vector2.y]]))

    _matrix: np.matrix = field()

    @property
    def as_vectors(self) -> tuple[pg.Vector2, pg.Vector2]:
        m = self._matrix
        return (pg.Vector2(m[0, 0], m[0, 1]),
                pg.Vector2(m[1, 0], m[1, 1]))

    @property
    def inverse(self) -> "Matrix2":
        return Matrix2(np.matrix(np.linalg.inv(self._matrix)))

    @_matrix.validator
    def _validate_matrix(self, _, matrix: np.matrix) -> None:
        if tuple(matrix.shape) != (2, 2):
            raise ValueError(f"Only 2x2 matrix supported")

    def apply(self, vector: pg.Vector2) -> pg.Vector2:
        array = np.array([vector.x, vector.y])
        transformed = array.dot(self._matrix).T
        return pg.Vector2(transformed[0], transformed[1])
