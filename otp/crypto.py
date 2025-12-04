from cryptography.fernet import Fernet
from app.settings import ENCRYPTION_KEY

fernet = Fernet(ENCRYPTION_KEY.encode())
def encrypt(value: str):
    """
    Encrypts the base32 key. 
    
    :param value: The base32 key itself.
    :type value: str
    """
    token = fernet.encrypt(value.encode())
    return token.decode()

def decrypt(value: str):
    """
    Decrypts the base32 key. 
    
    :param value: The encrypted base32 key
    :type value: str
    """
    text =  fernet.decrypt(value.encode())
    return text.decode()