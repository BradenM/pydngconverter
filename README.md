# PyDNGConverter

Python Interface for the Adobe's DNG Converter.

Utilizing parallel processing,
PyDNGConverter can convert RAW images to DNG up to **~60% faster** than simply utilizing Adobe's DNG Converter.

## Installation

```sh
pip install -U pydngconverter
```

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
