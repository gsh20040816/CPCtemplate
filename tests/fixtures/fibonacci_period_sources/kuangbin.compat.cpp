#include <bits/stdc++.h>
using namespace std;
long long gcd(long long a,long long b){
    if(b == 0)return a;
    return gcd(b,a%b);
}
long long lcm(long long a,long long b){
    return a/gcd(a,b)*b;
}
struct Matrix{
    long long mat[2][2];
};
Matrix mul_M(Matrix a,Matrix b,long long mod){
    Matrix ret;
    for(int i = 0;i < 2;i++)
        for(int j = 0;j < 2;j++){
            ret.mat[i][j] = 0;
            for(int k = 0;k < 2;k++){
                 ret.mat[i][j] += a.mat[i][k]*b.mat[k][j]%mod;
                 if(ret.mat[i][j] >= mod)ret.mat[i][j] -= mod;
            }
        }
    return ret;
}
Matrix pow_M(Matrix a,long long n,long long mod){
    Matrix ret;
    memset(ret.mat,0,sizeof(ret.mat));
    for(int i = 0;i < 2;i++)ret.mat[i][i] = 1;
    Matrix tmp = a;
    while(n){
        if(n&1)ret = mul_M(ret,tmp,mod);
        tmp = mul_M(tmp,tmp,mod);
        n >>= 1;
    }
    return ret;
}
long long pow_m(long long a,long long n,long long mod){ //a^b % mod
    long long ret = 1;
    long long tmp = a%mod;
    while(n){
        if(n&1)ret = ret*tmp%mod;
        tmp = tmp*tmp%mod;
        n >>= 1;
    }
    return ret;
}
//素数筛选和合数分解
const int MAXN = 1000000;
int prime[MAXN+1];
void getPrime(){
    memset(prime,0,sizeof(prime));
    for(int i = 2;i <= MAXN;i++){
        if(!prime[i])prime[++prime[0]] = i;
           for(int j = 1;j <= prime[0] && prime[j] <= MAXN/i;j++){
               prime[prime[j]*i] = 1;
               if(i%prime[j] == 0)break;
           }
    }
}
long long factor[100][2];
int fatCnt;
int getFactors(long long x){
    fatCnt = 0;
    long long tmp = x;
    for(int i = 1;prime[i] <= tmp/prime[i];i++){
        factor[fatCnt][1] = 0;
        if(tmp%prime[i] == 0){
            factor[fatCnt][0] = prime[i];
            while(tmp%prime[i] == 0){
                factor[fatCnt][1]++;
                tmp /= prime[i];
            }
            fatCnt++;
        }
    }
    if(tmp != 1){
        factor[fatCnt][0] = tmp;
        factor[fatCnt++][1] = 1;
    }
    return fatCnt;
}
//勒让德符号
int legendre(long long a,long long p){
    if(pow_m(a,(p-1)>>1,p) == 1)return 1;
    else return -1;
}
int f0 = 1;
int f1 = 1;
long long getFib(long long n,long long mod){
    if(mod == 1)return 0;
    Matrix A;
    A.mat[0][0] = 0;
    A.mat[1][0] = 1;
    A.mat[0][1] = 1;
    A.mat[1][1] = 1;
    Matrix B = pow_M(A,n,mod);
    long long ret = f0*B.mat[0][0] + f1*B.mat[1][0];
    return ret%mod;
}
long long fac[1000000];
long long G(long long p){
    long long num;
    if(legendre(5,p) == 1)num = p-1;
    else num = 2*(p+1);
    //找出 num 的所有约数
    int cnt = 0;
    for(long long i = 1;i*i <= num;i++)
        if(num%i == 0){
            fac[cnt++] = i;
            if(i*i != num)
                 fac[cnt++] = num/i;
        }
    sort(fac,fac+cnt);
    long long ans;
    for(int i = 0;i < cnt;i++){
        if(getFib(fac[i],p) == f0 && getFib(fac[i]+1,p) == f1){
            ans = fac[i];
            break;
        }
    }
    return ans;
}
long long find_loop(long long n){
    getFactors(n);
    long long ans = 1;
    for(int i = 0;i < fatCnt;i++){
        long long record = 1;
        if(factor[i][0] == 2)record = 3;
        else if(factor[i][0] == 3)record = 8;
        else if(factor[i][0] == 5)record = 20;
        else record = G(factor[i][0]);
        for(int j = 1;j < factor[i][1];j++)
            record *= factor[i][0];
        ans = lcm(ans,record);
    }
    return ans;
}
void init(){
    getPrime();
}
int main(){
    init();
    int T;
    int iCase = 0;
    int n;
    scanf("%d",&T);
    while(T--){
        iCase++;
        scanf("%d",&n);
        printf("Case #%d: %lld\n",iCase,find_loop(n));
    }
    return 0;
}
