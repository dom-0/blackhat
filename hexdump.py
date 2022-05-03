#!/usr/bin/env python3

hex = [(len(repr(i)) == 3) and chr(i) or '*' for i in range(1,256)]
print(hex)

ascii = hex = [(len(repr(i)) == 3) and ord(i) or '*' for i in range(1,256)]
print(ascii)