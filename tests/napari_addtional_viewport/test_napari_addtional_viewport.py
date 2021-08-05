"""
Unittests for napari_addtional_viewport.napari_addtional_viewport module.
"""
from unittest.mock import MagicMock
import sys

sys.modules['napari'] = MagicMock()
sys.modules['napari.utils'] = MagicMock()
sys.modules['napari.utils.notifications'] = MagicMock()
sys.modules['vispy'] = MagicMock()
sys.modules['magicgui.widgets'] = MagicMock()
import pytest
import numpy as np
import napari
from napari_additional_viewport.napari_additional_viewport import (AdditionalViewPortWidget, STARTING_CANVAS_WIDTH,
STARTING_CANVAS_HEIGHT)
from magicgui.events import Event, EventEmitter

class MockEvents():
    def __init__(self):
        """
        Minimal event set for MockedShapeLayer
        """
        self.highlight = EventEmitter()

class MockShapeLayer():
    """
    Mock of a napari shape layer.
    """
    def __init__(self):
        """
        Initilatize the MockEvents for slot registration
        """
        self.events = MockEvents()

    @property
    def selected_data(self):
        """
        Currently selected shapes id
        """
        return [0]

    @property
    def data(self):
        """
        Currently selected shapes
        """
        return [[[ -7., -5], [7,  -5], [0., 8]]]


class MockColormap():
    @property
    def name(self):
        """
        Return the mocked name property
        """
        return 'gray'

class MockImageLayer():
    """
    Mock of a napari shape layer.
    """
    def __init__(self, stack_size = 0):
        self.colormap = MockColormap()
        self.stack_size = stack_size

    @property
    def data(self):
        """
        Image layer data
        """
        if self.stack_size == 0:
            return np.ones((1024, 1024))
        else:
            return [np.ones((1024, 1024))] * self.stack_size

    @property
    def name(self):
        """
        Image Layer Name
        """

@pytest.fixture(scope='module')
def add_vp_widget():
    """
    Module-wide additional viewport widget.
    """
    # setup fixture
    return AdditionalViewPortWidget(napari.Viewer)
    # teardown fixture


def test_additional_viewport_widget(add_vp_widget, mocker):
    """
    Integration test for the napari_multiple_viewport.AdditionalViewPortWidget.
    """

    # Mocking a single image
    add_vp_widget.image_layer.value = MockImageLayer()
    # Manually invoking the callback set by image_layer.changed.connect
    add_vp_widget.image_layer.changed.callbacks[0](Event(""))
    assert(np.sum(add_vp_widget.image_layer.value.data) == 1024*1024)
    assert(add_vp_widget.image_layer.value.stack_size == 0)

    # Moking a z-stack with 3 napari_layers
    stack_size = 3
    add_vp_widget.image_layer.value = MockImageLayer(stack_size=stack_size)
    # Manually invoking the callback set by image_layer.changed.connect
    add_vp_widget.image_layer.changed.callbacks[0](Event(""))
    assert(np.sum(add_vp_widget.image_layer.value.data) == stack_size*1024*1024)
    assert(add_vp_widget.image_layer.value.stack_size == stack_size)

    # Mocking shape layer
    add_vp_widget.shape_layer.value = MockShapeLayer()
    # Manually invoking the callback set by image_layer.changed.connect
    add_vp_widget.shape_layer.changed.callbacks[0](Event(""))
    # Manually invocking the callback set by shape_layer.value.events.highlight.connect
    # The callbacks tuple is tuple of tuples
    #add_vp_widget.shape_layer.value.events.highlight.callbacks[0][0]().shape_highlight_callback(Event(""))
    #assert((add_vp_widget.minx, add_vp_widget.maxx, add_vp_widget.miny, add_vp_widget.maxy) == (-5, 8, -7, 7) )

    # There is no point in testing z_index callback, since the index is not manipulated
