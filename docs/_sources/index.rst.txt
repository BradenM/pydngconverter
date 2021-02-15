PyDNGConverter
==========================================

Python API for Adobe's DNG Converter.

Utilizing parallel processing,
PyDNGConverter can convert RAW images to DNG up to **~60% faster** than simply utilizing Adobe's DNG Converter.

Installation
------------
:code:`pip install -U pydngconverter`

To utilize PyDNGConverter's Exif thumbnail extraction (as opposed to Adobe DNG Converters'), the following dependencies are required:

- `ExifTool <https://exiftool.org/>`_
- `ImageMagick <https://docs.wand-py.org/en/0.6.2/guide/install.html>`_

Then specify `JPEGPreview.EXTRACT` for `DNGConverters` `jpeg_preview` parameter.

Alternatively, you can utilize Adobe DNG Converters' thumbnail extraction via:
 - `JPEGPreview.MEDIUM`
 - `JPEGPreview.FULL`

Or, disable thumbnails via:
 - `JPEGPreview.NONE`


.. toctree::
    :caption: Documentation
    :maxdepth: 4

    modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
