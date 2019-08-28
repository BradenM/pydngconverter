# PyDNGConverter

Python Interface for the Adobe's DNG Converter

> This project is very early on in development. It currently only supports .CR2 files.
>
> More documentation will come soon.


## Installation

```sh
pip install -U pydngconverter
```

## Example

```python
from pydngconverter import DNGConverter, JPEGPreview

# Create Instance
pydng = DNGConverter('/my/raw/files/',
                    dest='/dngfiles',
                    jpeg_preview=JPEGPreview.FULL,
                    fast_load=True,
                    multiprocess=True
                    )

# Convert all raw images
pydng.convert()

```
