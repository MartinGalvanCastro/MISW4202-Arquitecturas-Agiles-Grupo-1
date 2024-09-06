import os
debe_fallar = False

INSTANCE_TYPE = os.getenv('INSTANCE_TYPE', 'principal')

def set_fallar(valor):
    global debe_fallar
    debe_fallar = valor

def get_fallar():
    return debe_fallar and INSTANCE_TYPE == 'principal'