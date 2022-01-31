import random

from params import p
from params import g

def keygen():
    sk = 0
    pk = 0
    q = (p-1)/2
    sk = random.SystemRandom().randint(1,q)
    pk = pow(g, sk) % p
    print("keygen")
    return pk,sk

def encrypt(pk,m):
    c1 = 0
    c2 = 0
    q = (p-1)/2
    r = random.SystemRandom().randint(1,q)
    c1 = pow(g, r) % p
    c2 = (pow(pk, r) * m) % p
    print("encrypt")
    return [c1,c2]

# def decrypt(sk,c):
#     m = 0
    
#     m = (c[1] / pow(c[0], sk)) % p
#     print("decrypt")
#     return m

