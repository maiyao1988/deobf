# deobf
An experimental ollvm like deofuscator,aim to remove obfuscation made by ollvm like compiler, exspecially FLA to make reverse engineering easier...
[中文原理说明](./doc/deobf.md)
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

3.run python deobf.py <elf_path> <elf_out_path> <trace_path> <func_start_hex> <func_end_hex> <is_thumb> <type>
  - <elf_path> the input ELF to remove obfuscate
  - <elf_out_path> output ELF
  - <trace_path> the trace file path of the target function, which contains the instruction trace, can be collect by ida trace break point.there is an example file  tests/bin/data/ins-url.trc
   - <func_start_hex> the start offset of the target function 
   - <func_end_hex> the end offset of the target function
   - <is_thumb> 0/1 is the target function is thumb
   - \<type\> [optional] the detector type, not passing is ok for many case
 
 example 
   ```python deobf.py  tests/bin/libmakeurl2.4.9.so url.so tests/data/ins-url.trc 0x0000342C 0x00003668 1```
   - This should deobf libmakeurl2.4.9.so JNI_ONLoad, you can see the output url.so JNI_ONLoad, has been simplified.
   

## Dependencies
- [Keystone assembler framework](https://github.com/keystone-engine/keystone)

