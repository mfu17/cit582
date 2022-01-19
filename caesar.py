
def encrypt(key,plaintext):
    ciphertext=""
    for i in range(len(plaintext)):
        l = plaintext[i]
        ciphertext += chr((ord(l) + key - 65) % 26 + 65)
    #YOUR CODE HERE
    return ciphertext

def decrypt(key,ciphertext):
    plaintext=""
    #YOUR CODE HERE
    plaintext = encrypt(key - 26, ciphertext)
    return plaintext


