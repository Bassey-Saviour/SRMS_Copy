import bcrypt

password = "test123".encode()  # the password the student will use
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(hashed.decode())

