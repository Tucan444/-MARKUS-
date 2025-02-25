from scenes.SPECIAL.Effects.Effect import Effect
from scenes.SPECIAL.Effects.default.texture_calculator import TextureCalculator
from scripts.GameTypes import ColorNormalized, Percentage, OperationType, FloatDoubleFBO
from scripts.Utilities.Graphics.double_framebuffer import DoubleFramebuffer
from scripts.Utilities.Graphics.frag import Frag
from scripts.Utilities.Graphics.kernel import Kernel


class SobelEdges(Effect):
    def __init__(self, frag: Frag, preblur_pass_size: int=2,
                 edge_color: ColorNormalized=(1, 1, 1), edge_strength: float=1,
                 grayscale_edges: Percentage=1, edge_operation: OperationType=OperationType.EUCLID):
        super().__init__(frag)

        self.tex: DoubleFramebuffer = self.graphics.double_fbo
        self.calculation_target: FloatDoubleFBO = None
        self.box_blur: 'BoxBlur' = None
        self.pixel_transform: 'PixelTransform' = None
        self.edge_finalizer: 'PixelTransform' = None
        self.convolution_x: 'Convolution' = None
        self.convolution_y: 'Convolution' = None
        self.texture_calculator: 'TextureCalculator' = None

        self.preblur_pass_size: int = preblur_pass_size
        self.edge_color: ColorNormalized = edge_color
        self.edge_strength: float = edge_strength
        self.grayscale_edges: Percentage = grayscale_edges
        self.edge_operation: OperationType = edge_operation

    def init(self) -> None:
        self.box_blur = self.graphics.effects["box_blur"].clone
        self.pixel_transform = self.graphics.effects["pixel_transform"].clone
        self.edge_finalizer = self.pixel_transform.clone
        self.convolution_x = self.graphics.effects["convolution"].clone
        self.convolution_y = self.convolution_x.clone
        self.texture_calculator = self.graphics.effects["texture_calculator"].clone

        kernel: Kernel = Kernel(self.game)
        kernel.become_sobel_x()
        self.convolution_x.kernel = kernel.texture
        self.convolution_x.kernel_color_range = kernel.color_range

        kernel.become_sobel_y()
        self.convolution_y.kernel = kernel.texture
        self.convolution_y.kernel_color_range = kernel.color_range

    @property
    def clone(self) -> 'SobelEdges':
        edges = SobelEdges(self.frag, self.preblur_pass_size, self.edge_color, self.edge_strength,
                           self.grayscale_edges, self.edge_operation)
        edges.init()
        return edges

    def _update_frag(self) -> None:
        self.box_blur.tex = self.frag.target
        self.box_blur.blur_size = self.preblur_pass_size

        self.pixel_transform.tex = self.frag.target
        self.pixel_transform.grayscale = self.grayscale_edges

        self.edge_finalizer.tex = self.frag.target
        self.edge_finalizer.intensity = (
            self.edge_color[0] * self.edge_strength,
            self.edge_color[1] * self.edge_strength,
            self.edge_color[2] * self.edge_strength
        )

        self.texture_calculator.tex_a = self.calculation_target.front
        self.texture_calculator.tex_b = self.calculation_target.back
        self.texture_calculator.target = self.frag.target
        self.texture_calculator.operation = self.edge_operation

        self.convolution_x.tex = self.frag.target
        self.convolution_y.tex = self.frag.target

    def _configure_frag(self) -> None:
        self.box_blur.frag.target = self.frag.target
        self.pixel_transform.frag.flip_fbo = False
        self.pixel_transform.frag.target = self.frag.target

        self.texture_calculator.frag.flip_fbo = False

    def _execute_frag(self) -> None:
        self.box_blur.execute()
        self.pixel_transform.execute()

        self.convolution_x.frag.target = self.calculation_target
        self.convolution_x.execute()

        self.convolution_y.frag.target = self.calculation_target
        self.convolution_y.execute()

        #self.texture_calculator.target.flip_fbo = False
        self.texture_calculator.execute()

        self.edge_finalizer.frag.flip_fbo = False
        self.edge_finalizer.frag.target = self.frag.target
        self.edge_finalizer.execute()
