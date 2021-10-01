from setuptools import setup, find_packages


setup(
    name='fractal-napari-plugins-colletion:addtional_viewport',
    version='1.1.0',
    author='Dario Vischi, Marco Franzon, Giuseppe Piero Brandino',
    author_email='dario.vischi@fmi.ch, marco.franzon@exact-lab.it, giuseppe.brandino@exact-lab.it',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    license='BSD3',
    description=(
        'Widget to add an additional viewport, to visualize on a specific shape.'
    ),
    long_description=open('README.md').read(),
    python_requires='>=3.7',
    install_requires=[
        "napari[all] == 0.4.7",
        "napari_plugin_engine >= 0.1.9",
        "magicgui >= 0.2.9",
        "matplotlib >= 3.4.2",
        "dask[complete] >= 2021.4.0",
        "numpy >= 1.20.2",
        "imagecodecs >= 2020.5.30",
    ],
    entry_points={
        'napari.plugin': [
            'napari_additional_viewport = napari_additional_viewport.napari_additional_viewport'
        ],
    },
    setup_requires=['pytest-runner',],
    tests_require=['pytest',],

)
