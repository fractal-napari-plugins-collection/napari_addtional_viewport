Additional Viewport Widget
-----------------------------------------

This plugin adds and additional viewport, focused on a selected area from the main view.

To start the widget 

``Plugins`` -> ``Add Dock Widget`` -> ``Additional Viewport Widget``


This will add a dockable widget, with a viewport window and an interface

.. image:: ./additional_wp.png
  :width: 400
  :alt: Additional viewport widget


The ``shape layer`` dropdown will list all the available shape layer and allow to select one, while 
the ``image layer`` allows selection of the image layer to visualize.
Finally, the ``z-index`` slider allows, in the case of z-stacks, to move between z-layers.

Once a shape layer and an image layer are selected, using the napari shape selection tool will focus the addtional viewport
on the bouding box of the currently selected shape in the currently selected image layer
