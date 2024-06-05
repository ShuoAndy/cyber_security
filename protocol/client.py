import socket
import socket
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import DES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import random
import string

show_process = True

def client_program():
    host = '127.0.0.1'
    port = 65448
    pw = "sharekey"
    pw = pw.encode('utf-8')

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # step 1：Client端生成RSA密钥对，将公钥用口令DES加密后发给Server
    k_A = RSA.generate(2048)
    pk_A = k_A.publickey().exportKey()
    if show_process:
        print("pk_A:",pk_A)
    sk_A = k_A.exportKey()
    cipher_des = DES.new(pw, DES.MODE_ECB)
    msg1 = cipher_des.encrypt(pad(pk_A, DES.block_size))
    client_socket.send(msg1)

    # step 3：Client端收到Server端的会话密钥，生成随机数NA，用会话密钥对随机数DES加密后发给Server
    msg2 = client_socket.recv(1024)
    encrypted_k_s = cipher_des.decrypt(msg2)
    encrypted_k_s = unpad(encrypted_k_s, DES.block_size)
    sk_A = RSA.import_key(sk_A)
    cipher_rsa = PKCS1_v1_5.new(sk_A)
    k_s = cipher_rsa.decrypt(encrypted_k_s, None)
    if show_process:
        print("k_s:",k_s.decode('utf-8'))

    n_a = ''.join(random.choices(string.digits, k = 20))
    if show_process:
        print("n_a:",n_a)
    n_a = n_a.encode('utf-8')
    cipher_des = DES.new(k_s, DES.MODE_ECB)
    msg3 = cipher_des.encrypt(pad(n_a, DES.block_size))
    client_socket.send(msg3)
    
    # step 5：Client端收到Server端的两个随机数 N1||N2，验证N1是否等于NA。如果相等，将N2用会话密钥DES加密后发给Server
    msg4 = client_socket.recv(1024)
    concatenated = cipher_des.decrypt(msg4)
    concatenated = unpad(concatenated, DES.block_size)
    concatenated = concatenated.decode('utf-8')
    n_1 = concatenated[:20]  
    n_2 = concatenated[20:]  
    if show_process:
        print("n_b:",n_2)
    if n_1 == n_a.decode('utf-8'):
        msg5 = cipher_des.encrypt(pad(n_2.encode('utf-8'), DES.block_size))
        client_socket.send(msg5)
    else:
        print('认证失败')

    while True:
        msg = input('A端发送消息:')
        msg = cipher_des.encrypt(pad(msg.encode('utf-8'), DES.block_size))
        client_socket.send(msg)
        
        msg = client_socket.recv(1024)
        if not msg:
            break
        msg = cipher_des.decrypt(msg)
        msg = unpad(msg, DES.block_size)
        if not msg:
            break
        print('A端接收消息', msg.decode('utf-8'))

        

    client_socket.close()

if __name__ == '__main__':
    client_program()
