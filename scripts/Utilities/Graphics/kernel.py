import math

import pygame
from moderngl import Context, Texture
from pygame import Surface, Vector3, Vector2

from scripts.GameTypes import PixelPos, Color, Resolution, Byte, SignedByte, VectorColor


class Kernel:
    ZERO_MULTIPLIER: float = 127/255
    POSITIVE_N: Byte = 128
    NEGATIVE_N: Byte = 127

    ZERO: Byte = 127
    ZERO_TUPLE: tuple[Byte, Byte, Byte] = (127, 127, 127)
    ONE_TUPLE: tuple[Byte, Byte, Byte] = (128, 128, 128)
    VECTOR_ZERO: VectorColor = Vector3(127, 127, 127)

    def __init__(self, game: 'Game', color_range: float=255):
        self.game: 'Game' = game
        self.graphics: 'Graphics' = game.graphics
        self.ctx: Context = self.graphics.ctx

        self.color_range = color_range

        self.kernel: Surface = Surface((1, 1))
        self.kernel.fill(self.ONE_TUPLE)

        self.make_red: bool = True
        self.make_green: bool = True
        self.make_blue: bool = True

    @property
    def color_range_zero(self) -> Vector3:
        return Vector3(Kernel.ZERO_MULTIPLIER * self.color_range)

    @property
    def color_range_inverse(self) -> float:
        if self.color_range == 0:
            return 10**7

        return 1 / self.color_range

    def save(self) -> None:
        pygame.image.save(self.kernel, "kernel.png")

    def set_intensity(self, x_y: tuple[int, int], value: Byte):
        r, g, b, _ = self.kernel.get_at(x_y)

        if self.make_red:
            r = value
        if self.make_green:
            g = value
        if self.make_blue:
            b = value

        self.kernel.set_at(x_y, (r, g, b))

    def unsign_n(self, n: SignedByte) -> Byte:
        return n + self.ZERO

    def sign_n(self, n: Byte) -> SignedByte:
        return n - self.ZERO

    def unsign_tuple(self, n: SignedByte) -> Color:
        return n + self.ZERO, n + self.ZERO, n + self.ZERO

    def float_to_signed_byte(self, n: float) -> SignedByte:
        return max(-127, min(128, round(n / math.ceil(self.color_range * 0.5) * 128)))

    def float_to_unsigned_byte(self, n: float) -> SignedByte:
        return self.unsign_n(self.float_to_signed_byte(n))

    def unsigned_byte_to_float(self, n: Byte) -> float:
        n -= self.ZERO
        n /= 128
        n *= math.ceil(self.color_range * 0.5)
        return n

    def signed_byte_to_float(self, n: SignedByte) -> float:
        n /= 128
        n *= math.ceil(self.color_range * 0.5)
        return n

    def become_clear(self, size: Resolution):
        self.kernel = Surface(size)
        self.kernel.fill(self.ZERO_TUPLE)

        one: SignedByte = self.float_to_signed_byte(1)
        self.kernel.set_at((
            size[0] // 2, size[1] // 2
        ), self.unsign_tuple(one))

    def become_laplacian(self) -> None:
        self.color_range = 10
        self.become_clear((3, 3))
        self.set_intensity((1, 1), self.float_to_unsigned_byte(-4))
        self.set_intensity((0, 1), self.float_to_unsigned_byte(1))
        self.set_intensity((1, 0), self.float_to_unsigned_byte(1))
        self.set_intensity((1, 2), self.float_to_unsigned_byte(1))
        self.set_intensity((2, 1), self.float_to_unsigned_byte(1))

    def become_sharpen(self) -> None:
        self.color_range = 10
        self.become_clear((3, 3))
        self.set_intensity((1, 1), self.float_to_unsigned_byte(5))
        self.set_intensity((0, 1), self.float_to_unsigned_byte(-1))
        self.set_intensity((1, 0), self.float_to_unsigned_byte(-1))
        self.set_intensity((1, 2), self.float_to_unsigned_byte(-1))
        self.set_intensity((2, 1), self.float_to_unsigned_byte(-1))

    def become_gauss(self, size: int=3, standard_deviation: float=1) -> None:
        self.color_range = 2
        self.become_clear((size, size))

        gauss_func: callable = lambda x, y: math.e ** (-((x*x + y*y) / (2 * standard_deviation)))

        calculations = [[0. for _ in range(size)] for _ in range(size)]
        mid: Vector2 = Vector2(size) * 0.5
        total_fill: float = 0

        for x in range(size):
            for y in range(size):
                pos: Vector2 = Vector2(x, y) + Vector2(0.5, 0.5) - mid
                gauss: float = gauss_func(*pos)

                total_fill += gauss
                calculations[x][y] = gauss

        fill_norm: float = 1. / total_fill
        for x in range(size):
            for y in range(size):
                gauss: float = calculations[x][y] * fill_norm
                final_value: SignedByte = int(gauss * Kernel.POSITIVE_N)
                self.set_intensity((x, y), self.unsign_n(final_value))

    def become_sobel_x(self, clear_mid: bool=True):
        self.color_range = 5
        self.become_clear((3, 3))

        if clear_mid:
            self.set_intensity((1, 1), self.ZERO)

        self.set_intensity((0, 0), self.float_to_unsigned_byte(-1))
        self.set_intensity((0, 1), self.float_to_unsigned_byte(-2))
        self.set_intensity((0, 2), self.float_to_unsigned_byte(-1))

        self.set_intensity((2, 0), self.float_to_unsigned_byte(1))
        self.set_intensity((2, 1), self.float_to_unsigned_byte(2))
        self.set_intensity((2, 2), self.float_to_unsigned_byte(1))

    def become_sobel_y(self, clear_mid: bool=True):
        self.color_range = 5
        self.become_clear((3, 3))

        if clear_mid:
            self.set_intensity((1, 1), self.ZERO)

        self.set_intensity((0, 0), self.float_to_unsigned_byte(-1))
        self.set_intensity((1, 0), self.float_to_unsigned_byte(-2))
        self.set_intensity((2, 0), self.float_to_unsigned_byte(-1))

        self.set_intensity((0, 2), self.float_to_unsigned_byte(1))
        self.set_intensity((1, 2), self.float_to_unsigned_byte(2))
        self.set_intensity((2, 2), self.float_to_unsigned_byte(1))

    def become_sobel_u(self, clear_mid: bool=True):
        self.color_range = 5
        self.become_clear((3, 3))

        if clear_mid:
            self.set_intensity((1, 1), self.ZERO)

        self.set_intensity((1, 0), self.float_to_unsigned_byte(-1))
        self.set_intensity((0, 0), self.float_to_unsigned_byte(-2))
        self.set_intensity((0, 1), self.float_to_unsigned_byte(-1))

        self.set_intensity((1, 2), self.float_to_unsigned_byte(1))
        self.set_intensity((2, 2), self.float_to_unsigned_byte(2))
        self.set_intensity((2, 1), self.float_to_unsigned_byte(1))

    def become_sobel_v(self, clear_mid: bool=True):
        self.color_range = 5
        self.become_clear((3, 3))

        if clear_mid:
            self.set_intensity((1, 1), self.ZERO)

        self.set_intensity((0, 1), self.float_to_unsigned_byte(-1))
        self.set_intensity((0, 2), self.float_to_unsigned_byte(-2))
        self.set_intensity((1, 2), self.float_to_unsigned_byte(-1))

        self.set_intensity((1, 0), self.float_to_unsigned_byte(1))
        self.set_intensity((2, 0), self.float_to_unsigned_byte(2))
        self.set_intensity((2, 1), self.float_to_unsigned_byte(1))

    def is_valid_position(self, position: PixelPos) -> bool:
        if len(position) != 2:
            return False

        if position[0] < 0 or position[0] >= self.kernel.width:
            return False

        if position[1] < 0 or position[1] >= self.kernel.height:
            return False

        return True

    @property
    def texture(self) -> Texture:
        return self.graphics.surface_to_texture(self.kernel, repeat=True)

    def __matmul__(self, other: 'Kernel') -> 'Kernel':
        new_kernel: Kernel = Kernel(self.game)

        new_width: int = self.kernel.width + other.kernel.width - 1
        new_height: int = self.kernel.height + other.kernel.height - 1

        new_kernel.kernel = Surface((new_width, new_height))
        new_kernel.color_range = self.color_range * other.color_range

        for i in range(new_width):
            for j in range(new_height):
                color: VectorColor = Vector3()

                for x in range(other.kernel.width):
                    for y in range(other.kernel.height):
                        sample_position: PixelPos = [i - x, j - y]
                        if not self.is_valid_position(sample_position):
                            continue

                        r0, g0, b0, _ = self.kernel.get_at((i - x, j - y))
                        r1, g1, b1, _ = other.kernel.get_at((x, y))

                        my_color: VectorColor = Vector3(
                            self.unsigned_byte_to_float(r0),
                            self.unsigned_byte_to_float(g0),
                            self.unsigned_byte_to_float(b0))
                        other_color: VectorColor = Vector3(
                            other.unsigned_byte_to_float(r1),
                            other.unsigned_byte_to_float(g1),
                            other.unsigned_byte_to_float(b1))

                        color += Vector3(
                            my_color.x * other_color.x,
                            my_color.y * other_color.y,
                            my_color.z * other_color.z
                        )

                red: SignedByte = new_kernel.float_to_unsigned_byte(color.x)
                green: SignedByte = new_kernel.float_to_unsigned_byte(color.y)
                blue: SignedByte = new_kernel.float_to_unsigned_byte(color.z)
                new_kernel.kernel.set_at((i, j), (red, green, blue))

        return new_kernel

    @property
    def as_string(self) -> str:
        return (f"kernel: {self.kernel.get_size()}, "
                f"color range: {self.color_range}, "
                f"make red: {self.make_red}, "
                f"make green: {self.make_green}, "
                f"make blue: {self.make_blue}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string
