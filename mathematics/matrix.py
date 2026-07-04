import numpy as np
from attrs import frozen, field

from mathematics.vector import Vector2


@frozen
class Matrix2:
    @classmethod
    def from_vectors(cls, vector1: Vector2, vector2: Vector2) -> "Matrix2":
        return cls(np.matrix([[vector1.x, vector1.y],
                              [vector2.x, vector2.y]]))

    _matrix: np.matrix = field()

    @_matrix.validator
    def _validate_matrix(self, _, matrix: np.matrix) -> None:
        if tuple(matrix.shape) != (2, 2):
            raise ValueError(f"Only 2x2 matrix supported")

    @property
    def as_vectors(self) -> tuple[Vector2, Vector2]:
        m = self._matrix
        return (Vector2(m[0, 0], m[0, 1]),
                Vector2(m[1, 0], m[1, 1]))

    @property
    def inverse(self) -> "Matrix2":
        return Matrix2(np.matrix(np.linalg.inv(self._matrix)))

    def apply(self, vector: Vector2) -> Vector2:
        array = np.array([vector.x, vector.y])
        transformed = array.dot(self._matrix).T
        return Vector2(transformed[0], transformed[1])
