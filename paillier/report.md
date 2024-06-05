# 第 5 章 同态加密匿名投票 

计12 王嘉硕

### 环境设置

### 环境设置
```
Python 3.8.17
```

### 实验内容

实现具有加法同态性质的 Paillier 算法，对投票人的投票信息进行加密。公私钥和加解密过程参照教材P170实现即可。对于生成公私钥：

- 生成两个大素数 p, q，且满足 gcd(pq,(p-1)(q-1))=1。
- 计算 N = p * q 和 λ = lcm(p-1, q-1)。
- 选择随机数 g，能保证 μ = (L(g^λ mod N^2))^(-1) mod N 存在。
- 生成公钥 pk = (n, g)，私钥 sk = (λ, μ)。

代码如下：

```
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
```

对于加解密：

- 加密过程为：选择随机数 r，计算 c = g^m * r^n mod N^2。
- 解密过程为：计算 m = L(c^λ mod N^2) * μ mod N。

代码如下：

```
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
```

### 实验结果

我们生成公私钥后，对投票信息进行加密，然后进行解密。对于五个投票人（投票情况为[1, 0, 1, 1, 0]），结果为：

```
投票密文: [3938602470238653, 6421614264618248, 7674930992017787, 8736606120980312, 8861899331788497]
投票明文: 3
```