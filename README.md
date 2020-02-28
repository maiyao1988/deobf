# deobf
ollvm like deofuscator,aim to remove obfuscate maked by ollvm like compiler, exspecially FLA to make reverse engineering easier...
 
## Usage

> In the future this will be possible through pypi.

Make sure you are using python 3.7.

1. Clone the repository
2. Run `pip install -r requirements.txt`

> If you have trouble getting the `keystone-engine` dependency on Windows (as I did):
> 1. Clone their [repository](https://github.com/keystone-engine/keystone)
> 2. Open a terminal in `bindings/python`
> 3. Run `python setup.py install` (Make sure you are using python 3.7)
> 4. Download their `Windows - Core engine` package [here](http://www.keystone-engine.org/download/) for your python arch.
> 5. Put the `keystone.dll` in `C:\location_to_python\Lib\site-packages\keystone\`.

## Dependencies
- [Keystone assembler framework](https://github.com/keystone-engine/keystone)

