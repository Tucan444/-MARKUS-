from enum import Enum

import pygame
from moderngl import Texture, Framebuffer
from pygame import Vector3
from pygame.math import Vector2

from scripts.DataStructures.matrices import Matrix2D, Matrix3D
from scripts.DataStructures.rays import Ray

# types below

Resolution = tuple[int, int]

# discrete positions
PixelPos = list[int]

PixelDisplayPos = PixelPos
PixelWorldPos = PixelPos


# continous positions
Position = Vector2

DisplayPosition = Position
FocusedPosition = Position  # is centered around camera center, as if its 0, 0
WorldPosition = Position

# vectors

Vector = Vector2
PixelVec = list[int]

DisplayVector = Vector
FocusedVector = Vector
WorldVector = Vector

PixelDisplayVec = PixelVec
PixelFocusedVec = PixelVec
PixelWorldVec = PixelVec

# rects
Rect = pygame.FRect | pygame.Rect
DisplayRect = Rect
WorldRect = Rect

# tiles

GridPosition = Position
GridRect = Rect
TilePosition = tuple[int, int]
OffgridTilePosition = tuple[float, float]
TileHitInfo = tuple[float, 'Tile']

# ui

UISheetPosition = Position
UISheetVector = Position
class HitboxType(Enum):
    RECTANGLE=0
    ELLIPSE=1
    CIRCLE=2

# events

SortableFunction = tuple[float, str, callable] | tuple[float, str, callable, object]
SF_key = lambda x: x[0]

# rays
DisplayRay = Ray
WorldRay = Ray
GridRay = Ray
NormalizedGridRay = GridRay
UiSheetRay = Ray

# screen loop
ScreenLoopPosition = Vector2
ScreenLoopVector = Vector2

# time
Time = float
RealTime = Time
WorldTime = Time
TimelineTime = Time

# moderngl
UV_Position = Position
UVN_Position = Position
ClipPosition = Position

UV_Vector = Position
UVN_Vector = Position
ClipVector = Position

class CommandType(Enum):
    EFFECT=0
    DISPLAY_BLIT=1
    FRAG=2

Viewport = tuple[float, float, float, float]
ShaderAttributes = dict[str, tuple|Texture|list|Vector2|Vector3|Matrix2D|Matrix3D|Framebuffer]
FloatDoubleFBO = 'DoubleFramebuffer'

# kernel
Byte = int
SignedByte = int

# effects
class PrisonShape(Enum):
    NO_SHAPE: int = 0
    CIRCLE: int = 1
    SQUARE: int = 2
    DIAMOND: int = 3
class OperationType(Enum):
    ADD = 0
    SUBTRACT = 1
    MULTIPLY = 2
    DIVIDE = 3
    EUCLID = 4
    MANHATTAN = 5
    CHESS = 6
    ANGLE = 7

# other

Color = tuple[int, int, int]
VectorColor = Vector3
ColorNormalized = tuple[float, float, float]
Percentage = float
RealPercentage = float
Angle = float
HyperAngle = float
Shear = tuple[Vector2, bool]
Index = int
Range = Position
IntRange = PixelPos | Resolution
Subspace = Vector
Scaling = Vector
Done = bool
Success = bool
Detected = bool

# general

Mutable2 = Vector2 | list[int]
Comp2 = Vector2 | list[int] | tuple[int, int]

# functions to convert below

def Position_2_PixelPos(position: Position) -> PixelPos:
    return [int(position.x // 1), int(position.y // 1)]

def PixelPos_2_Position(pixelPos: PixelPos | Resolution) -> Position:
    return Vector2(pixelPos[0], pixelPos[1])