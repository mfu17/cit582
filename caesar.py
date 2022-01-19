
def encrypt(key,plaintext):
    ciphertext=""
    #YOUR CODE HERE
#     for i in range(len(plaintext)):
#         l = plaintext[i]
#         ciphertext += chr((ord(l) + key - 65) % 26 + 65)
    for l in plaintext:
#         l = plaintext[i]
        ciphertext += chr((ord(l) + key - 65) % 26 + 65)        
    return ciphertext

def decrypt(key,ciphertext):
    plaintext=""
    #YOUR CODE HERE
    plaintext = encrypt(26 - key, ciphertext)
    
    return plaintext
