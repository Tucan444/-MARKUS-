from pygame.math import Vector2, Vector3
from math import sin, cos, sinh, cosh
from array import array

class Matrix2D:
    def __init__(self, i: Vector2, j: Vector2):
        self.i: Vector2 = i
        self.j: Vector2 = j

    def set_value(self, row: int, column: int, value: float):
        if column == 0:
            self.i[row] = value
        elif column == 1:
            self.j[row] = value

    def apply_on_vector(self, vector: Vector2) -> Vector2:
        return vector.x * self.i + vector.y * self.j

    def before(self, matrix: 'Matrix2D') -> 'Matrix2D':
        new_i: Vector2 = matrix.apply_on_vector(self.i)
        new_j: Vector2 = matrix.apply_on_vector(self.j)

        self.i = new_i
        self.j = new_j

        return self

    def after(self, matrix: 'Matrix2D') -> 'Matrix2D':
        new_i: Vector2 = self.apply_on_vector(matrix.i)
        new_j: Vector2 = self.apply_on_vector(matrix.j)

        self.i = new_i
        self.j = new_j

        return self

    def copy(self) -> 'Matrix2D':
        return Matrix2D(
            Vector2(*self.i.xy),
            Vector2(*self.j.xy)
        )

    @classmethod
    def get_identity(cls) -> 'Matrix2D':
        return Matrix2D(
            Vector2(1, 0),
            Vector2(0, 1)
        )

    @classmethod
    def get_scale(cls, x_scale: float, y_scale: float) -> 'Matrix2D':
        return Matrix2D(
            Vector2(x_scale, 0),
            Vector2(0, y_scale)
        )

    @classmethod
    def get_shear(cls, x_shear: float, y_shear: float, x_first: bool=True) -> 'Matrix2D':
        x_shear_matrix: Matrix2D = Matrix2D(
            Vector2(1, x_shear),
            Vector2(0, 1)
        )

        y_shear_matrix: Matrix2D = Matrix2D(
            Vector2(1, 0),
            Vector2(y_shear, 1)
        )

        if x_first:
            x_shear_matrix.before(y_shear_matrix)
        else:
            x_shear_matrix.after(y_shear_matrix)

        return x_shear_matrix

    @classmethod
    def get_rotation(cls, alpha: float) -> 'Matrix2D':
        return Matrix2D(
            Vector2(cos(alpha), sin(alpha)),
            Vector2(-sin(alpha), cos(alpha))
        )

    @classmethod
    def get_hyperbolic_rotation(cls, alpha: float) -> 'Matrix2D':
        return Matrix2D(
            Vector2(cosh(alpha), sinh(alpha)),
            Vector2(sinh(alpha), cosh(alpha))
        )

    @property
    def as_string(self) -> str:
        return (f"|{self.i.x}, {self.j.x}|"
                f"|{self.i.y}, {self.j.y}|")

    def __str__(self):
        return self.as_string

    def __repr__(self):
        return self.as_string

    @property
    def as_array(self) -> array:
        return array('f', [
            self.i.x, self.j.x,
            self.i.y, self.j.y
        ])

class Matrix3D:
    def __init__(self, i: Vector3, j: Vector3, k: Vector3):
        self.i: Vector3 = i
        self.j: Vector3 = j
        self.k: Vector3 = k

    def set_value(self, row: int, column: int, value: float):
        if column == 0:
            self.i[row] = value
        elif column == 1:
            self.j[row] = value
        elif column == 2:
            self.k[row] = value

    def apply_on_vector(self, vector: Vector3) -> Vector3:
        return vector.x * self.i + vector.y * self.j + vector.z * self.k

    def before(self, matrix: 'Matrix3D') -> 'Matrix3D':
        new_i: Vector3 = matrix.apply_on_vector(self.i)
        new_j: Vector3 = matrix.apply_on_vector(self.j)
        new_k: Vector3 = matrix.apply_on_vector(self.k)

        self.i = new_i
        self.j = new_j
        self.k = new_k

        return self

    def after(self, matrix: 'Matrix3D') -> 'Matrix3D':
        new_i: Vector3 = self.apply_on_vector(matrix.i)
        new_j: Vector3 = self.apply_on_vector(matrix.j)
        new_k: Vector3 = self.apply_on_vector(matrix.k)

        self.i = new_i
        self.j = new_j
        self.k = new_k

        return self

    def copy(self) -> 'Matrix3D':
        return Matrix3D(
            Vector3(*self.i.xyz),
            Vector3(*self.j.xyz),
            Vector3(*self.k.xyz)
        )

    @classmethod
    def get_identity(cls) -> 'Matrix3D':
        return Matrix3D(
            Vector3(1, 0, 0),
            Vector3(0, 1, 0),
            Vector3(0, 0, 1)
        )

    @classmethod
    def get_scale(cls, x_scale: float, y_scale: float, z_scale: float) -> 'Matrix3D':
        return Matrix3D(
            Vector3(x_scale, 0, 0),
            Vector3(0, y_scale, 0),
            Vector3(0, 0, z_scale)
        )

    @classmethod
    def get_shear(cls, x_shear: float, y_shear: float, z_shear: float, order: tuple[int, int, int]=(0, 1, 2)) -> 'Matrix3D':
        x_shear_matrix: Matrix3D = Matrix3D(
            Vector3(1, 0, 0),
            Vector3(x_shear, 1, 0),
            Vector3(x_shear, 0, 1)
        )

        y_shear_matrix: Matrix3D = Matrix3D(
            Vector3(1, y_shear, 0),
            Vector3(0, 1, 0),
            Vector3(0, y_shear, 1)
        )

        z_shear_matrix: Matrix3D = Matrix3D(
            Vector3(1, 0, z_shear),
            Vector3(0, 1, z_shear),
            Vector3(0, 0, 1)
        )

        matrices: list[Matrix3D] = [None, None, None]
        matrices[order[0]] = x_shear_matrix
        matrices[order[1]] = y_shear_matrix
        matrices[order[2]] = z_shear_matrix

        assert(None not in matrices)

        matrices[1].after(matrices[0])
        matrices[2].after(matrices[1])

        return matrices[2]

    @property
    def as_string(self) -> str:
        return (f"|{self.i.x}, {self.j.x}, {self.k.x}|"
                f"|{self.i.y}, {self.j.y}, {self.k.y}|"
                f"|{self.i.z}, {self.j.z}, {self.k.z}|")

    def __str__(self):
        return self.as_string

    def __repr__(self):
        return self.as_string

    @property
    def as_array(self) -> array:
        return array('f', [
            self.i.x, self.j.x, self.k.x,
            self.i.y, self.j.y, self.k.y,
            self.i.z, self.j.z, self.k.z
        ])
