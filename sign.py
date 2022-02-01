from fastecdsa.curve import secp256k1
from fastecdsa.keys import export_key, gen_keypair, gen_private_key

from fastecdsa import curve, ecdsa, keys, point
from hashlib import sha256

#import random

def sign(m):
	#generate public key
	#Your code here
#	G = ecdsa.secp256k1
#	n = G.order()
	#d = random.SystemRandom().randint(1,n)
	#fastecdsa.keys.gen_keypair(secp256k1)
	d = gen_private_key(secp256k1)
	public_key = d * secp256k1.G

	#generate signature
	#Your code here
	r = 0
	s = 0

	[r,s] = ecdsa.sign(m, d, secp256k1, sha256)

	assert isinstance( public_key, point.Point )
	assert isinstance( r, int )
	assert isinstance( s, int )
	return( public_key, [r,s] )


