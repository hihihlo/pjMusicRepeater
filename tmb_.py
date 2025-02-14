import os, sys

class Tmb:
    def __init__(self):
        self.ma = 11
        self.mb = 22

def fna(obj: Tmb):
    obj.ma += 1

m = Tmb()
print(m.ma)
fna(m)
print(m.ma)
