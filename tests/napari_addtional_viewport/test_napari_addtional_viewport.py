"""
Unittests for napari_addtional_viewport.napari_addtional_viewport module.
"""
from unittest.mock import MagicMock
import sys

sys.modules['vispy'] = MagicMock()
import pytest
import numpy as np
import napari
from napari_additional_viewport.napari_additional_viewport import \
    AdditionalViewPortWidget, STARTING_CANVAS_WIDTH, STARTING_CANVAS_HEIGHT
from magicgui.events import Event, EventEmitter, EmitterGroup


class MockViewer():
    """
    Mock of a napari viewer.
    """
    @property
    def window(self):
        """
        Viewer window.
        """
        return MagicMock()


class MockShapeLayer():
    """
    Mock of a napari shape layer.
    """
    def __init__(self):
        """
        Initialization method.
        """
        self.events = EmitterGroup(
            source=self,
            auto_connect=False,
            highlight=Event
        )
        self._selected_data = []

    @property
    def selected_data(self):
        """
        Get currently selected shapes IDs.
        """
        return self._selected_data
    
    @selected_data.setter
    def selected_data(self, selected_data):
        """
        Set currently selected shapes IDs.
        """
        self._selected_data = selected_data
        self.events.highlight()  # invoke events

    @property
    def data(self):
        """
        Shape layer data.
        """
        return [[[ -7., -5], [7,  -5], [0., 8]]]


class MockColormap():
    """
    Mock of a colormap.
    """
    @property
    def name(self):
        """
        Name of the colormap.
        """
        return 'gray'


class MockImageLayer():
    """
    Mock of a napari shape layer.
    """
    def __init__(self, stack_size = 0):
        """
        Initialization method.
        """
        self.colormap = MockColormap()
        self.stack_size = stack_size

    @property
    def data(self):
        """
        Image layer data.
        """
        if self.stack_size == 0:
            return np.ones((1024, 1024))
        else:
            return [np.ones((1024, 1024))] * self.stack_size

    @property
    def name(self):
        """
        Name of the image layer.
        """
        return "MockImageLayer"


@pytest.fixture(scope='module')
def add_vp_widget():
    """
    Module-wide additional viewport widget.
    """
    # setup fixture
    add_vp_widget = AdditionalViewPortWidget(MockViewer())
    yield add_vp_widget
    # teardown fixture
    pass


"""
def test_event_emitter(add_vp_widget, mocker):
    i = []
    test_emitter = EventEmitter(source=None, type="test_emitter", event_class=Event)
    @test_emitter.connect
    def on_update_layer(event):
        i.append(event.value)
    test_emitter(value=42)
    assert i[0] == 42
"""


def test_additional_viewport_widget(add_vp_widget, mocker):
    """
    Integration test for the napari_multiple_viewport.AdditionalViewPortWidget.
    """
    # initialize layers
    mock_image_layer_1 = MockImageLayer()
    mock_image_layer_2 = MockImageLayer(stack_size=3)
    mock_shape_layer = MockShapeLayer()

    add_vp_widget.image_layer.choices = [mock_image_layer_1, mock_image_layer_2]
    add_vp_widget.shape_layer.choices = [mock_shape_layer]

    # Test unstacked image layer
    add_vp_widget.image_layer.value = mock_image_layer_1
    assert(np.sum(add_vp_widget.image_layer.value.data) == 1024*1024)
    assert(add_vp_widget.image_layer.value.stack_size == 0)

    # Test stacked image layer
    add_vp_widget.image_layer.value = mock_image_layer_2
    assert(np.sum(add_vp_widget.image_layer.value.data) == 3 * 1024 * 1024)
    assert(add_vp_widget.image_layer.value.stack_size == 3)

    # Test shape layer
    add_vp_widget.shape_layer.value = mock_shape_layer
    assert(
        (add_vp_widget.minx, add_vp_widget.maxx, add_vp_widget.miny, add_vp_widget.maxy) ==
        (0, STARTING_CANVAS_WIDTH, 0, STARTING_CANVAS_WIDTH)
    )
    mock_shape_layer.selected_data = [0]
    assert(
        (add_vp_widget.minx, add_vp_widget.maxx, add_vp_widget.miny, add_vp_widget.maxy) ==
        (-5, 8, -7, 7)
    )

    # There is no point in testing z_index callback, since the index is not manipulated
