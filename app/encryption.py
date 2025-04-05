from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Hash import SHA256


def hash_with_salt(texto):
    # Generar un salt aleatorio
    salt = get_random_bytes(16)

    # Convertir el texto en claro a bytes
    texto_bytes = texto.encode()

    # Crear un objeto de hash SHA-256
    hash_object = SHA256.new()

    # Agregar la sal y el texto plano al hash
    hash_object.update(salt + texto_bytes)

    # Calcular el hash final
    hash_FI = hash_object.hexdigest()

    return hash_FI


def decrypt_aes(texto_cifrado_str, nonce_str, tag_str, clave):
    # Convertir el texto cifrado, nonce y tag de cadena de texto a bytes
    texto_cifrado = bytes.fromhex(texto_cifrado_str)
    nonce = bytes.fromhex(nonce_str)
    tag = bytes.fromhex(tag_str)

    # Crear un objeto AES con la clave y el nonce proporcionados
    cipher = AES.new(clave, AES.MODE_EAX, nonce=nonce)

    # Descifrar el texto con el tag
    texto_descifrado = cipher.decrypt_and_verify(texto_cifrado, tag)

    # Convertir los bytes del texto descifrado a una cadena de texto
    texto_descifrado_str = texto_descifrado.decode()
    
    return texto_descifrado_str


def encrypt_aes(texto, clave):
    # Convertir el texto a bytes
    texto_bytes = texto.encode()

    # Crear un objeto AES con la clave proporcionada
    cipher = AES.new(clave, AES.MODE_EAX)

    # Cifrar el texto
    nonce = cipher.nonce
    texto_cifrado, tag = cipher.encrypt_and_digest(texto_bytes)

    # Convertir el texto cifrado en bytes a una cadena de texto
    texto_cifrado_str = texto_cifrado.hex()
    tag_str = tag.hex()

    # Devolver el texto cifrado, el nonce y el tag
    return texto_cifrado_str, nonce.hex(), tag_str


if __name__ == '__main__':
    texto = "Hola Mundo"
    clave = get_random_bytes(16)
    
    # Cifrar el texto
    texto_cifrado, nonce, tag = encrypt_aes(texto, clave)
    print("Texto cifrado: " + texto_cifrado)
    print("Nonce: " + nonce)
    print("Tag: " + tag)
    
    # Descifrar el texto
    des = decrypt_aes(texto_cifrado, nonce, tag, clave)
    print("Texto descifrado: " + des)
