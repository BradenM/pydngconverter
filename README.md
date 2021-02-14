# PyDNGConverter

Python Interface for the Adobe's DNG Converter.

Utilizing parallel processing,
PyDNGConverter can convert RAW images to DNG up to **~60% faster** than simply utilizing Adobe's DNG Converter.

## Installation

```sh
pip install -U pydngconverter
```

To utilize PyDNGConverter's Exif thumbnail extraction (as opposed to Adobe DNG Converters'), the following dependencies are required:
- [ExifTool](https://exiftool.org/)
- [ImageMagick](https://docs.wand-py.org/en/0.6.2/guide/install.html)

Then specify `JPEGPreview.EXTRACT` for `DNGConverters` `jpeg_preview` parameter.

Alternatively, you can utilize Adobe DNG Converters' thumbnail extraction via:
 - `JPEGPreview.MEDIUM`
 - `JPEGPreview.FULL`

Or, disable thumbnails via:
 - `JPEGPreview.NONE`

## Example

```python
import asyncio
from pydngconverter import DNGConverter, flags

async def main():
    # Create converter instance.
    pydng = DNGConverter('/my/raw/files/',
                        dest='/dngfiles',
                        jpeg_preview=flags.JPEGPreview.EXTRACT,
                        fast_load=True,
                        )
    # Convert all
    return await pydng.convert()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()

```
