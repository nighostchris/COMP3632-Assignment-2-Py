import sys
import subprocess
import random

# calling padding oracle function
def padding_oracle(random_block):
    f = open("oraclebyte", "wb")
    for i in range(0, 32):
        f.write(chr(random_block[i]))
<<<<<<< HEAD
    result = subprocess.check_output(["python", "oracle", "oraclebyte"])
=======
    result = subprocess.check_output("python oracle ciphertext")
>>>>>>> d215d5982973380991f153b9462be07b06b7722d
    if result == "1":
        return True
    return False

# taking in 16 bytes of ciphertext
def decrypt_byte(y):
    print "decrypt_byte"
    random_block = []

    # generate first random 15 bytes in integer
    for i in range(0, 15):
        random_block.append(random.randint(0, 256))

    # initialize i as 0 and concatentate with y
    random_block.append(0)
    random_block += y

    # check with padding oracle until returns true
    while padding_oracle(random_block) == False:
        random_block[15] += 1

    # repeat replacing the first 15 bytes until padding oracle returns true for all bytes
    for i in range(0, 15):
        random_block[i] = random.randint(0, 256)
        if padding_oracle(random_block) == False:
            return random_block[15] ^ (17 - (i + 1))    # return i xor 17 - the kth random byte
    return random_block[15] ^ 1                         # return i xor 1 if always return true

def decrypt_block(y):
    print "decrypt_block"
    decrypted_block = []
    random_block = []

    # generate random block
    for i in range(0, 15):
        random_block.append(random.randint(0, 256))
        decrypted_block.append("")
    random_block.append(0)
    random_block += y
    decrypted_block.append(decrypt_byte(y))          # last byte decrypted from y

    # replace the random byte from the byte we want to decrypt
    for i in range(14, -1, -1):
        for j in range(15, i, -1):
            random_block[j] = decrypted_block[j] ^ (17 - (i + 1))   # replacing byte greater than i
        random_block[i] = 0;                                        # initially i is 0
        while padding_oracle(random_block) == False:
            random_block[i] += 1
        decrypted_block[i] = random_block[i] ^ (17 - (i + 1))
    return decrypted_block

def decrypt(iv, y):
    plaintext = []

    # decrypt block by block from the end except the first block
    for i in range(len(y)-1, 0, -1):
        temp = []
        decrypted_block = decrypt_block(y[i])                       # get yi
        for j in range(0, 16):
            temp.append(decrypted_block[j] ^ y[i-1][j])             # byte by byte xor previous non-decrypt block
        plaintext.append(temp)
    
    #handle the first block
    temp = []
    decrypted_block = decrypt_block(y[0])
    for i in range(0, 16):
        temp.append(decrypted_block[i] ^ iv[i])
    plaintext.append(temp)
    return plaintext

# input the ciphertext file
try:
    filename = sys.argv[1]
    f = open(filename, "rb")
except:
    print "ciphertext file cannot be open."
    sys.exit(1)

ctext = f.read()

# get the iv and ciphertext in integer form
temp_iv = ctext[0:16]
iv = []
for i in range(0, 16):
    iv.append(ord(temp_iv[i]))

print iv

ciphertext = ctext[16:]
temp_num = []
for i in range(0, len(ciphertext)):
    temp_num.append(ord(ciphertext[i]))
ciphertext = [temp_num[i:i+16] for i in range(0, len(temp_num), 16)]

print ciphertext

# print the result plaintext
plaintext = decrypt(iv, ciphertext)
print plaintext
output = []
for i in range(0, len(plaintext)):
    for j in range(0, 16):
        output.append(chr(plaintext[i][j]))
print output
