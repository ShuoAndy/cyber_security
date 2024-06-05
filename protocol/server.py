import socket
import socket
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import DES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import random
import string

show_process = True

def server_program():
    # 获取本地主机名和端口
    host = '127.0.0.1'
    port = 65448
    pw = "sharekey"
    pw = pw.encode('utf-8')

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    conn, address = server_socket.accept()

    # step 2：Server端收到Client的公钥，随机生成会话密钥，用Client的公钥RSA加密会话密钥，再用口令再次DES加密，发送给Client
    msg1 = conn.recv(1024)
    cipher_des = DES.new(pw, DES.MODE_ECB)
    pk_A = cipher_des.decrypt(msg1)
    pk_A = unpad(pk_A, DES.block_size)
    if show_process:
        print("pk_A:",pk_A)
    pk_A = RSA.import_key(pk_A)

    k_s = ''.join(random.choices(string.ascii_letters + string.digits, k = 8))
    if show_process:
        print("k_s:",k_s)
    k_s = k_s.encode('utf-8')
    cipher_rsa = PKCS1_v1_5.new(pk_A)
    encrypted_k_s = cipher_rsa.encrypt(k_s)
    msg2 = cipher_des.encrypt(pad(encrypted_k_s, DES.block_size))
    conn.send(msg2)
    

    # step 4：Server端收到Client端的随机数NA，生成随机数NB后将二者拼接，用会话密钥DES加密后发给Client
    msg3 = conn.recv(1024)
    cipher_des = DES.new(k_s, DES.MODE_ECB)
    n_a = cipher_des.decrypt(msg3)
    n_a = unpad(n_a, DES.block_size)
    n_a = n_a.decode('utf-8')
    if show_process:
        print("n_a:",n_a)
    n_b = ''.join(random.choices(string.digits, k = 20))
    if show_process:
        print("n_b:",n_b)
    concatenated = n_a + n_b
    concatenated = concatenated.encode('utf-8')
    msg4 = cipher_des.encrypt(pad(concatenated, DES.block_size))
    conn.send(msg4)


    # step 6：Server端收到Client端的随机数N2，验证N2是否等于NB，如果相等，验证通过
    msg5 = conn.recv(1024)
    n_2 = cipher_des.decrypt(msg5)
    n_2 = unpad(n_2, DES.block_size)
    n_2 = n_2.decode('utf-8')
    
    if n_2 == n_b:
        print('认证成功')
    else:
        print('认证失败')

    # 此时验证通过，可以进行后续通信
    while True:
        msg = conn.recv(1024)
        if not msg:
            break
        msg = cipher_des.decrypt(msg)
        msg = unpad(msg, DES.block_size)
        print('B端接收消息', msg.decode('utf-8'))

        msg = input('B端发送消息:')
        msg = cipher_des.encrypt(pad(msg.encode('utf-8'), DES.block_size))
        conn.send(msg)



    
    conn.close()

if __name__ == '__main__':
    server_program()
