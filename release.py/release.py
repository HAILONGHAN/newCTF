import os,random,sys,string
from hashlib import sha256
import SocketServer
import signal
from Crypto.Util.number import *
from gmpy2 import *
FLAG = '1212'

def p_Builder():
    pi = getPrime(15)
    qi = getPrime(15)
    print pi
    print qi
    return pi*qi
p = 2^128-7
#global p
def i(x):
    #print '[*]gcd: '+str(GCD(x,p))
    return invert(x,p)

def check_point(A):
    (u,v) = A
    if (u**3+14*u+1)%p == (v**2)%p:
        return 1
    else:
        return 0
def add(A,B):
    assert check_point(A)==1 and check_point(B) == 1
    (u,v),(w,x) = A,B
    assert u!=w or v == x
    if u == w:
        m = (3*u*w+14)*i(v+x)
    else:
        m = (x-v)*i(w-u)
    y = m*m - u - w
    z = m*(u-y) - v
    return y % p, z % p

def sub(A,B):
    assert check_point(A)==1 and check_point(B) == 1
    (u,v),(w,x) = A,B
    if u > w and v > x:
        return abs(u-w,v-x)
    elif v < x:
        return abs(u-w,v-x+p)
    else:
        return abs(u-w+p,v-x)
    

def mul(t,A,B=0):
    assert check_point(A)==1
    #assert B==0 or check_point(B)==1
    if not t:
        #print B
        return B
    else:
        return mul(t//2, add(A,A), B if not t&1 else add(B,A) if B else A)

def div(t,A,B=0):
    assert check_point(A)==1 and check_point(B) == 1
    (u,v),(w,x) = A,B
    (y,z) = sub(A,B) 
    if not t:
        return B
    elif z == 0 :
        return B
    else:
        return (y/t,z/t)

    
class Task(SocketServer.BaseRequestHandler):
    def proof_of_work(self):
        random.seed(os.urandom(8))
        proof = ''.join([random.choice(string.ascii_letters+string.digits) for _ in xrange(20)])
        digest = sha256(proof).hexdigest()
        self.request.send("sha256(XXXX+%s) == %s\n" % (proof[4:],digest))
        self.request.send('Give me XXXX:')
        x = self.request.recv(10)
        x = x.strip()
        if len(x) != 4 or sha256(x+proof[4:]).hexdigest() != digest: 
            return False
        return True
    def recvnum(self,sz):
        try:
            print sz
            r = sz
            res =""
            while r>0:
                res += self.request.recv(r)
                if res.endswith('\n'):
                    r = 0
                else:
                    r = sz - len(res)
            res = res.strip()
            t = int(res)
        except:
            res = ''
            t = 0
        return t
    def recvpoint(self, sz):
        try:
            r = sz
            res = ''
            while r>0:
                res += self.request.recv(r)
                if res.endswith('\n'):
                    r = 0
                else:
                    r = sz - len(res)
            res = res.strip()
            str1 = res.split(',')[0]
            str2 = res.split(',')[-1]
            assert str1 != str2
            x = int(str1.replace('(','').strip())
            y = int(str2.replace(')','').strip())
            #res = res.decode('hex')
        except:
            res = ''
            x = 0
            y = 0
        return (x,y)
    
    def dosend(self, msg):
        try:
            self.request.sendall(msg)
        except:
            pass

    def menu(self):
        #self.dosend("Welcome to the baby RSA-CURVES system!\n")
        #self.dosend("here are some options!\n")
        self.dosend("1. ADD.\n")
        self.dosend("2. SUB.\n")
        self.dosend("3. MUL.\n")
        self.dosend("4. DIV.\n")
        self.dosend("5. EXIT\n")
        self.dosend("input>> ")
    
    def ADD(self):
        self.dosend('input point A: \n')
        A = self.recvpoint(30)
        self.dosend('input point B: \n')
        B = self.recvpoint(30)
        C = add(A,B)
        self.dosend("the result is :"+str(C)+'\n')

    def SUB(self):
        self.dosend('Under Construction!\n')

    def MUL(self):
        self.dosend('input point A: \n')
        A = self.recvpoint(30)
        self.dosend('input number t: \n')
        t = self.recvnum(10)
        
        B = mul(t,A)
        self.dosend("the result is :"+str(B)+'\n')

    def DIV(self):
        self.dosend('input point A: \n')
        A = self.recvpoint(30)
        self.dosend('input point B: \n')
        B = self.recvpoint(30)
        self.dosend('input number t: \n')
        t = self.recvnum(10)
        C = div(t,A,B)
        self.dosend("the result is :"+str(C)+'\n')

    def handle(self):
        #if not self.proof_of_work():
            #return
        #signal.alarm(30)
        self.dosend("Welcome to BABY CURVES FACTOR SYSTEM!\n")
        self.dosend("here are some options!\n")
        global p
        p = p_Builder()
        print p 
        P = (1,4)
        assert check_point(P) == 1
        try:
            for j in xrange(1000):
                #print "done"
                self.menu() 
                r = self.recvnum(4)
                if r == 1:
                    self.ADD()
                elif r==2:
                    self.SUB()
                elif r==3:
                    self.MUL()
                elif r==4:
                    self.DIV()
                elif r==5:
                    break

        except:
            self.dosend(">.<\n")
        self.dosend("please give me a point(pi,qi): \n")
        R = self.recvpoint(30)
        (u,v) = R
        print R
        if u*v == p:
            self.dosend("%s\n" % FLAG)
        else:
            self.dosend(">.<\n")
        self.request.close()

class ForkingServer(SocketServer.ForkingTCPServer, SocketServer.TCPServer):
    pass


if __name__ == "__main__":
    HOST, PORT = '127.0.0.1', 10004
    print HOST
    print PORT
    server = ForkingServer((HOST, PORT), Task)
    server.allow_reuse_address = True
    server.serve_forever()
