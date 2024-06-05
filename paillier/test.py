import random
from math import gcd
from sympy import mod_inverse

def lcm(a, b):
    return abs(a*b) // gcd(a, b)

def L(x, n):
    return (x - 1) // n

class Paillier:
    def __init__(self, bit_length):
        self.bit_length = bit_length
        self.generate_keys()
    
    # 生成公钥和私钥
    def generate_keys(self):
        p = self.generate_prime()
        q = self.generate_prime()
        self.n = p * q
        self.n_sq = self.n * self.n
        self.lambda_ = lcm(p-1, q-1)
        self.g = random.randint(1, self.n_sq - 1)

        self.mu = mod_inverse(L(pow(self.g, self.lambda_, self.n_sq), self.n), self.n)
        
        self.public_key = (self.n, self.g)
        self.private_key = (self.lambda_, self.mu)
    
    def generate_prime(self):
        while True:
            prime = random.getrandbits(self.bit_length)
            if self.is_prime(prime) and prime > 100:
                return prime
    
    def is_prime(self, num):
        if num < 2:
            return False
        for _ in range(20):
            a = random.randint(1, num - 1)
            if pow(a, num - 1, num) != 1:
                return False
        return True
    
    def encrypt(self, m):
        n, g = self.public_key
        r = random.randint(1, n - 1)
        c = (pow(g, m, self.n_sq) * pow(r, n, self.n_sq)) % self.n_sq
        return c
    
    def decrypt(self, c):
        lambda_, mu = self.private_key
        n = self.n
        n_sq = self.n_sq
        x = pow(c, lambda_, n_sq)
        m = (L(x, n) * mu) % n
        return m

if __name__ == "__main__":
    paillier = Paillier(16)
    
    # 模拟选民的投票
    votes = [1, 0, 1, 1, 0]
    
    encrypted_votes = [paillier.encrypt(vote) for vote in votes]
    
    encrypted_result = encrypted_votes[0]
    for encrypted_vote in encrypted_votes[1:]:
        encrypted_result = (encrypted_result * encrypted_vote) % paillier.n_sq
    
    decrypted_result = paillier.decrypt(encrypted_result)
    
    print(f"投票密文: {encrypted_votes}")
    print(f"投票明文: {decrypted_result}")
