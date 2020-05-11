import hashlib

def pass_hashing(pwd):
	pwd = pwd.encode()
	h_pass= hashlib.sha256(pwd)
	return h_pass.hexdigest()

def pass_verify(pass_sha256, clear_pass):
	h_pass = pass_hashing(clear_pass)
	if (h_pass == pass_sha256):
		return True
	else:
		return False
