import os
import sys
import subprocess

# Call oracle function to check validity of r|yN
# return true if oracle returns 1
def padding_oracle(rplusyN):
	# write the 32 bytes to file call oraclebyte for checking
	f = open("oraclebyte", "wb")
	f.write(rplusyN)
	f.close()

	# call oracle function
	result = subprocess.check_output("python oracle oraclebyte", shell=True)
	if (int(result) == 1):
		return True
	return False

# get the i value upon success of padding oracle check
def get_byte_i(r, k, y):
	# generate first 15 random bytes
	i = 0
	r = r[:k-1] + chr(i) + r[k:]

	# concat with the block y which consists of 16 bytes
	rplusyN = r + y
	result = padding_oracle(rplusyN)

	# keep increase i until padding oracle returns valid result
	while (result == False):
		i += 1
		rplusyN = r[:k-1] + chr(i) + r[k:] + y
		result = padding_oracle(rplusyN)
	return (i, rplusyN)

def decrypt_byte(y):
	# generate first 15 random bytes
	r = bytearray(os.urandom(15)) + chr(0)
	(i, rplusyN) = get_byte_i(r, 16, y)

	# keep replacing byte start from r0
	replace = 0
	k = replace + 1
	newrplusyN = bytearray(os.urandom(1)) + rplusyN[1:]
	result = padding_oracle(newrplusyN)
	while ((result == True) and (k < 15)):
		replace += 1
		k = replace + 1
		newrplusyN = newrplusyN[:replace] + bytearray(os.urandom(1)) + newrplusyN[replace+1:]
		result = padding_oracle(newrplusyN)
	replace += 1
	return (i ^ (17 - replace - 1), r)

def decrypt_block(y, number):
	# D(yN)
	decrypted_block = bytearray(16)
	# xN
	plaintext_block = bytearray(16)
	
	# get the last decrypted byte and get the last plaintext char
	(decrypted_block[15], r) = decrypt_byte(y)
	plaintext_block[15] = decrypted_block[15] ^ int(ciphertext[number-1][15].encode('hex'), 16)

	# decrypt one block = 16 bytes
	for k in range(15, 0, -1):
		r = r[:k-1] + chr(0)
		for m in range(k, 16):
			r = r + chr(decrypted_block[m] ^ (17 - k))
		(i, rplusyN) = get_byte_i(r, k, y)

		decrypted_block[k-1] = i ^ (17 - k)
		plaintext_block[k-1] = decrypted_block[k-1] ^ int(ciphertext[number-1][k-1].encode('hex'), 16)

	for j in range(len(plaintext_block)):
		answer[(number-1) * 16 + j] = chr(plaintext_block[j])

# decrypt all blocks except the iv
def decrypt():
	for block in range(len(ciphertext)-1, 0, -1):
		decrypt_block(ciphertext[block], block)

# input the ciphertext file
try:
	filename = sys.argv[1]
	f = open(filename, "rb")
except:
	print "Ciphertext file cannot be opened."
	sys.exit(1)

ctext = f.read()
f.close()

# Split the ciphertext into blocks of 16 bytes
ciphertext = []
for i in range(0, len(ctext), 16):
	ciphertext.append(ctext[i:i+16])

# open up an array to store answer
answer = bytearray(len(ctext) - 16)

# start decrypt
decrypt()
	
# output plaintext
answer = "".join(chr(i) for i in answer)
print "Plaintext: " + answer