def passSalt(strPassword):
    import random

    strRandSalt = ''.join(chr(val) for val in random.sample(range(48,90),4))
    strSaltedPass = strPassword + strRandSalt

    return strSaltedPass, strRandSalt

def passHash(strSaltedPass):
    import hashlib

    hash = hashlib.sha512()
    hash.update(strSaltedPass.encode("utf-8"))
    strPassHash = hash.hexdigest()

    return strPassHash
