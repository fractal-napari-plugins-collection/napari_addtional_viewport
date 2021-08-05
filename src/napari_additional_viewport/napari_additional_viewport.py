"""
Main module containing the widget to create additional viewport
"""
import numpy as np

from vispy import scene

import napari
from napari_plugin_engine import napari_hook_implementation

from magicgui.widgets import FunctionGui

STARTING_CANVAS_WIDTH = 400
STARTING_CANVAS_HEIGHT = 400


def get_stack_size(layer):
    """
    Utility function that tries to understand if the image is a z-stack,
    a multiscale of numpy array.
    Since napari store z-stacks and multiscale images as lists of numpy arrays,
    if the data in the layer is not a numpy array, then we can distinguish between
    a z-stack and a multiscale image by comparing for example the sizes of the
    first two layers.

    :param layer: The viewer image layer to analyse
    """
    if not isinstance(layer.data, np.ndarray):
        if layer.data[0].shape == layer.data[1].shape:
            return len(layer.data)
    return 0


def get_data(layer, bbox):
    """
    Extracts the viewport array slice from the last selected shapes.
    Since napari uses lists of numpy arrays for both z-stacks and multiscale images,
    if the data are numpy arrays we assume it is an image.
    Otherwise we use an element of the list as image data.

    :param layer: The viewer image layer to read the data from
    :param bbox: The bounding box around the data to extract
    """
    minx, maxx, miny, maxy, minz, _ = bbox
    if isinstance(layer.data, np.ndarray):
        return layer.data[miny:maxy, minx:maxx]

    return layer.data[minz][miny:maxy, minx:maxx]


class AdditionalViewPortWidget(FunctionGui):
    # pylint: disable=R0901
    """
    MagicGUI ContainerWidget to open an additional viewport.
    """
    def __init__(self, viewer: napari.Viewer, name="additional_viewport", **kwargs):
        """
        Initialization method.

        :param viewer: The napari viewer.
        :param name: The name of the widget.
        :param kwargs: Additional keyworded arguments.
        """
        super().__init__(
            AdditionalViewPortWidget.apply,
            call_button=False,
            layout="vertical",
            param_options={
                "z_index": {"widget_type": "IntSlider", 'max': 0}
            },
            name=name
        )

        self.viewer = viewer
        self.minx = 0
        self.maxx = STARTING_CANVAS_WIDTH
        self.miny = 0
        self.maxy = STARTING_CANVAS_HEIGHT
        self.image = None

        '''
        canvas = scene.SceneCanvas(
            keys=None, vsync=True, size=(STARTING_CANVAS_WIDTH, STARTING_CANVAS_HEIGHT),
            show=False
        )
        canvas.title = 'Detail view of an individual cell'
        canvas.native.setMinimumSize(200, 200)
        canvas.context.set_depth_func('lequal')
        self.view = canvas.central_widget.add_view()

        # Set 2D camera (the camera will scale to the contents in the scene)
        self.view.camera = scene.PanZoomCamera(aspect=1)
        self.view.camera.flip = (0, 1, 0)  # flip y-axis to have correct aligment

        self.viewer.window.add_dock_widget(canvas.native, area='right', name='Additional viewport')
        '''
        @self.image_layer.changed.connect
        def on_update_image_layer(event):
            # pylint: disable=W0613
            """
            Callback method for change events on the layer combobox.

            :param event: The change event.
            """
            stack_size = get_stack_size(self.image_layer.value)
            if stack_size > 1:
                self.z_index.max = stack_size - 1
            else:
                self.z_index.max = 0
            self.display_slice()

        @self.shape_layer.changed.connect
        def on_update_shape_layer(event):
            # pylint: disable=W0613
            """
            Callback method for change events on the shape_layer combobox.

            :param event: The change event.
            """
            self.shape_layer.value.events.highlight.connect(self.shape_highlight_callback)
            self.display_slice()

        @self.z_index.changed.connect
        def on_update_z_index(event):
            # pylint: disable=W0613
            """
            Callback method for change events on the z-index slider.

            :param event: The change event.
            """
            if not self.shape_layer.value or not self.image_layer.value:
                return
            self.display_slice()

        self.native.layout().addStretch()

    def __setitem__(self, key, value):
        """Prevent assignment by index."""
        raise NotImplementedError("magicgui.Container does not support item setting.")

    def shape_highlight_callback(self, event):
        # pylint: disable=W0613
        """
        Callback fired when one or more shape is selected. Only
        the bounding box of the last one is used (to avoid too large
        textures and run into OpenGL issues)

        :param event: The change event.
        """
        if len(self.shape_layer.value.selected_data) == 0:
            return

        shape_id = list(self.shape_layer.value.selected_data)[-1]

        shape_coords = np.round(self.shape_layer.value.data[shape_id])

        # if we have a stack of images, also the shape have a z dimensional
        # that needs to be stripped down
        if shape_coords.shape[1] > 2:
            shape_coords = shape_coords[:, 1:3]

        if len(shape_coords) < 3:
            # while drawing a shape, the highlight events is fired for every point added,
            # but this could causes to access zero-size array, which will cause issues when
            # we draw the image with scene.visualts.Image
            # Therefore, we avoid changing the viewport until there are at least 3 points.
            return
        [self.miny, self.minx] = shape_coords.min(axis=0).astype(int)
        [self.maxy, self.maxx] = shape_coords.max(axis=0).astype(int)

        self.display_slice()

        self.shape_layer.value.status = "Selected shape '%s'." % shape_id

    def display_slice(self):
        """
        Displays the selected image slice in the canvas.
        """
        if self.image_layer.value is None:
            return

        bbox = self.minx, self.maxx, self.miny, self.maxy, self.z_index.value, self.z_index.value
        data = get_data(self.image_layer.value, bbox)
        cmap = self.image_layer.value.colormap.name

        if self.image:
            self.image.parent = None
        self.image = scene.visuals.Image(
            data, interpolation='nearest',
            parent=self.view.scene,
            cmap=cmap
        )

        self.view.camera.rect = (0, 0, self.maxx-self.minx, self.maxy-self.miny)

    @staticmethod
    def apply(shape_layer: "napari.layers.Shapes", image_layer: "napari.layers.Image", z_index=0):
        """
        Function executed when pressing the widget's call button.

        :param shape_layer: The shape layer where to read the ROIs from
        :param image_layer: The image layer where to read the data from
        :param z_index: The current z-index to visualize
        """


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    """
    Napari plugin that returns a widget for reading features from a CSV file.

    :return: An AdditionalViewPortWidget class
    """
    return AdditionalViewPortWidget
