import hashlib

def generate_subscribe_token(path,size):
    """
       Generate a token for the subscribe/unsubscribe to the topic contained in "path".
       The token is a substring of the md5 hash of the path.
       The size of the token is specified(in bytes) as parameter 

    """
    md5 = hashlib.md5(path.encode('utf-8')) 
    token=md5.hexdigest()
    return token[0:size]
