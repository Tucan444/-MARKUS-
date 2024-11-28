from pygame import Vector3
from math import *
import math
from scripts.DataStructures.matrices import Matrix3D

CartesianPosition = Vector3
SphericalPosition = Vector3
Angles = Vector3

class E3Rotation(Matrix3D):
    axis2index = {
        "x": 0,
        "y": 1,
        "z": 2
    }

    def __init__(self, i: CartesianPosition, j: CartesianPosition, k: CartesianPosition):
        super().__init__(i, j, k)

    def reverse_self(self) -> None:
        new_i = Vector3(self.i.x, self.j.x, self.k.x)
        new_j = Vector3(self.i.y, self.j.y, self.k.y)
        new_k = Vector3(self.i.z, self.j.z, self.k.z)

        self.i = new_i
        self.j = new_j
        self.k = new_k

    def rotate_vector(self, v: Vector3) -> Vector3:
        return self.apply_on_vector(v)

    @staticmethod
    def Spherical2Cartesian(v: Vector3) -> Vector3:
        position: Vector3 = Vector3()

        position[0] = cos(v.x) * cos(v.y)
        position[2] = sin(v.x) * cos(v.y)
        position[1] = sin(v.y)

        return position * v.z

    @staticmethod
    def Cartesian2Spherical(v: Vector3) -> Vector3:
        position: Vector3 = Vector3()
        position[2] = v.length()

        v = v.normalize()

        position[1] = asin(v.y)
        cosOfz = cos(v.y)
        position[0] = atan2(v.z / cosOfz, v.x / cosOfz)

        return position

    @classmethod
    def _flattenation(cls, v: Vector3) -> 'E3Rotation':
        beta = 0
        if v.x != 1:
            beta = math.atan2(v.y, v.z)

        flat = cls.plane(beta, "yz")

        return flat

    @classmethod
    def angles(cls, angles: Angles) -> 'E3Rotation':
        identity = cls.get_identity()

        alpha = identity.copy()
        beta = identity.copy()
        gamma = identity.copy()

        calculations = [0 for _ in range(6)]

        for i in range(3):
            calculations[i * 2] = math.cos(angles[i])
            calculations[i * 2 + 1] = math.sin(angles[i])

        alpha.i = Vector3(0, calculations[0], -calculations[1])
        alpha.j = Vector3(0, calculations[1], calculations[0])

        beta.i = Vector3(calculations[2], 0, -calculations[3])
        beta.k = Vector3(calculations[3], 0, calculations[2])

        gamma.i = Vector3(calculations[4], -calculations[5], 0)
        gamma.j = Vector3(calculations[5], calculations[4], 0)

        orientation = alpha.before(beta).before(gamma)
        return orientation

    @classmethod
    def plane(cls, angle: float, axis: str) -> 'E3Rotation':
        rot = cls.get_identity()

        one = cls.axis2index[axis[0]]
        two = cls.axis2index[axis[1]]

        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        rot.set_value(one, one, cos_angle)
        rot.set_value(two, two, cos_angle)
        rot.set_value(one, two, -sin_angle)
        rot.set_value(two, one, sin_angle)

        return rot

    @classmethod
    def point(cls, vec: Vector3) -> 'E3Rotation':
        v: Vector3 = cls.Cartesian2Spherical(vec)

        three = [
            cls.plane(v.x, "xz"),
            cls.plane(v.y, "xy")
        ]

        final = three[1]
        final.after(three[0])

        return final

    @classmethod
    def from_a_to_b(cls, angle: float, a: Vector3, b: Vector3) -> 'E3Rotation':
        to_a = cls.point(a)
        ato_origin = to_a.copy()
        ato_origin.reverse_self()

        v = ato_origin.rotate_vector(b)
        flat = cls._flattenation(v)
        unflat = flat.copy()
        unflat.reverse_self()

        final = ato_origin
        final.before(flat)
        final.before(cls.plane(angle, "xz"))
        final.before(unflat)
        final.before(to_a)

        return final

    @classmethod
    def angle_axis(cls, angle: float, axis: Vector3) -> 'E3Rotation':
        to_axis = cls.point(axis)
        axis_to_origin = to_axis.copy()
        axis_to_origin.reverse_self()

        final = axis_to_origin
        final.before(cls.plane(angle, "yz"))
        final.before(to_axis)

        return final
