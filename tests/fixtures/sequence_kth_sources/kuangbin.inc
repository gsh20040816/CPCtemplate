const int MAXN = 70010;
namespace Splay{
    struct Node *null;
    struct Node{
        Node *ch[2],*fa;
        int size,key,cnt;
        inline void setc(Node *p,int d){
            ch[d] = p;
            p->fa = this;
        }
        inline bool d(){
            return fa->ch[1] == this;
        }
        inline void push_up(){
                 size = ch[0]->size + ch[1]->size + cnt;
             }
             void clear(int _key){
                 size = cnt = 1;
                 key = _key;
                 ch[0] = ch[1] = fa = null;
             }
             inline bool isroot(){
                 return fa == null || this != fa->ch[0] && this != fa-> ch[1];
             }
      };
      Node pool[MAXN*20],*tail;
      Node *bc[MAXN*20];
      int bc_top;//内存回收
      void init(){
          tail = pool;
          bc_top = 0;
          null = tail++;
          null->size = null->cnt = 0;
          null->ch[0] = null->ch[1] = null->fa = null;
      }
      inline void rotate(Node *x){
          Node *f = x->fa, *ff = x->fa->fa;
          int c = x->d(), cc = f->d();
          f->setc(x->ch[!c],c);
          x->setc(f,!c);
          if(ff->ch[cc] == f)ff->setc(x,cc);
          else x->fa = ff;
          f->push_up();
      }
      inline void splay(Node* &root,Node* x,Node* goal){
          while(x->fa != goal){
              if(x->fa->fa == goal)rotate(x);
              else {
                  bool f = x->fa->d();
                  x->d() == f ? rotate(x->fa) : rotate(x);
                  rotate(x);
              }
          }
          x->push_up();
          if(goal == null)root = x;
      }
      //找到 r 子树里面的最左边那个
      Node* get_left(Node* r){
          Node* x = r;
          while(x->ch[0] != null)x = x->ch[0];
          return x;
      }
      //在 root 的树中删掉 x
      void erase(Node* &root,Node* x){
             splay(root,x,null);
             Node* t = root;
             if(t->ch[1] != null){
                 root = t->ch[1];
                 splay(root,get_left(t->ch[1]),null);
                 root->setc(t->ch[0],0);
             }
             else root = root->ch[0];
             bc[bc_top++] = x;
             root->fa = null;
             if(root != null)root->push_up();
      }
      Node* newNode(int key){
          Node* p;
          if(bc_top)p = bc[--bc_top];
          else p = tail++;
          p->clear(key);
          return p;
      }
      //插入一个值 key
      void insert(Node* &root,int key){
          if(root == null){
              root = newNode(key);
              return;
          }
          Node* now = root;
          Node* pre = root->fa;
          while(now != null){
              if(now->key == key){
                   now->cnt++;
                   splay(root,now,null);
                   return;
              }
              pre = now;
              now = now->ch[key >= now->key];
          }
          Node *x = newNode(key);
          pre->setc(x,key >= pre->key);
          splay(root,x,null);
      }
      //删除一个值 key
      void erase(Node* &root,int key){
          Node* now = root;
          while(now->key != key){
              now = now->ch[key >= now->key];
          }
          now->cnt--;
          if(now->cnt == 0)erase(root,now);
          else splay(root,now,null);
      }
      void Travel(Node* r){
        if(r == null)return;
        Travel(r->ch[0]);
        bc[bc_top++] = r;
        Travel(r->ch[1]);
    }
    void CLEAR(Node* &root){
        Travel(root);
        root = null;
    }
    //查询小于等于 val 的个数
    int query(Node *root,int val){
        int ans = 0;
        Node *x = root;
        while(x != null){
            if(val < x->key)x = x->ch[0];
            else{
                 ans += x->ch[0]->size + x->cnt;
                 x = x->ch[1];
            }
        }
        return ans;
    }
};
namespace ScapeGoatTree{
    const double alpha = 0.75;
    struct Node{
        Node *ch[2];
        int size,nodeCount,key;
        Splay::Node *root;
        bool isBad(){
            return ch[0]->nodeCount > alpha*nodeCount+5 || ch[1]-> nodeCount > alpha*nodeCount+5;
        }
        void push_up(){
            size = 1+ch[0]->size+ch[1]->size;
            nodeCount = 1+ch[0]->nodeCount+ch[1]->nodeCount;
        }
    };
    Node pool[MAXN];
    Node *tail,*root,*null;
    Node *bc[MAXN];
    int bc_top;
    void init(){
        tail = pool;
        null = tail++;
        null->ch[0] = null->ch[1] = null;
        null->size = null->nodeCount = 0;
        null->root = Splay::null;
        bc_top = 0;
    }
    inline Node* newNode(int key){
             Node *p;
             if(bc_top)p = bc[--bc_top];
             else p = tail++;
             p->key = key;
             p->ch[0] = p->ch[1] = null;
             p->size = p->nodeCount = 1;
             p->root = Splay::null;
             return p;
      }
      Node *buildTree(int *a,int l,int r){
          if(l >= r)return null;
          int mid = (l+r)/2;
          Node *p = newNode(a[mid]);
          for(int i = l;i < r;i++)
              Splay::insert(p->root,a[i]);
          p->ch[0] = buildTree(a,l,mid);
          p->ch[1] = buildTree(a,mid+1,r);
          p->push_up();
          return p;
      }
      void Travel(Node *p,vector<int>&v){
          if(p == null)return;
          Travel(p->ch[0],v);
          v.push_back(p->key);
          Splay::CLEAR(p->root);
          bc[bc_top++] = p;
          Travel(p->ch[1],v);
      }
      Node *divide(vector<int>&v,int l,int r){
          if(l == r)return null;
          int mid = (l+r)/2;
          Node *p = newNode(v[mid]);
          for(int i = l;i < r;i++)
              Splay::insert(p->root,v[i]);
          p->ch[0] = divide(v,l,mid);
          p->ch[1] = divide(v,mid+1,r);
          p->push_up();
          return p;
      }
      inline void rebuild(Node *&p){
          vector<int>v;
          Travel(p,v);
          p = divide(v,0,v.size());
      }
      //将第 id 个值修改为 val
      int Modify(Node *p,int id,int val){
          if(id == p->ch[0]->size+1){
              int v = p->key;
              Splay::erase(p->root,v);
              Splay::insert(p->root,val);
              p->key = val;
                 return v;
             }
             int res;
             if(p->ch[0]->size >= id)
                 res = Modify(p->ch[0],id,val);
             else res = Modify(p->ch[1],id-p->ch[0]->size-1,val);
             Splay::erase(p->root,res);
             Splay::insert(p->root,val);
             return res;
      }
      Node **insert(Node *&p,int id,int val){
          if(p == null){
              p = newNode(val);
              Splay::insert(p->root,val);
              return &null;
          }
          else {
              p->size++;
              p->nodeCount++;
              Splay::insert(p->root,val);
              Node ** res;
              if(id <= p->ch[0]->size+1)
                  res = insert(p->ch[0],id,val);
              else res = insert(p->ch[1],id-p->ch[0]->size-1,val);
              if(p->isBad())res = &p;
              return res;
          }
      }
      void insert(int id,int val){
          Node **p = insert(root,id,val);
          if(*p != null)rebuild(*p);
      }
      //查询在 [l,r] 区间，值小于等于 val 的个数
      int query(Node *p,int l,int r,int val){
          if(p == null)return 0;
          if(l <= 1 && p->size <= r)
              return Splay::query(p->root,val);
          else {
              int ans = 0;
              if(l <= p->ch[0]->size)
                  ans += query(p->ch[0],l,r,val);
              if(r > p->ch[0]->size+1)
                  ans += query(p->ch[1],l-p->ch[0]->size-1,r-p->ch [0]->size-1,val);
              if(p->key <= val && l <= p->ch[0]->size+1 && p->ch[0]-> size+1 <= r)
                  ans++;
              return ans;
          }
      }
      int query(int L,int R,int k){
             int ans;
             int l = 0, r = 100000;
             while(l <= r){
                 int mid = (l+r)/2;
                 if(query(root,L,R,mid) >= k){
                     ans = mid;
                     r = mid-1;
                 }
                 else l = mid+1;
             }
             return ans;
      }
  };
  int a[MAXN];
  int main()
  {
      int n;
      while(scanf("%d",&n) == 1){
          Splay::init();
          ScapeGoatTree::init();
          for(int i = 0;i < n;i++)scanf("%d",&a[i]);
          ScapeGoatTree::root = ScapeGoatTree::buildTree(a,0,n);
          int m;
          char op[10];
          scanf("%d",&m);
          int ans = 0;
          while(m--){
               scanf("%s",op);
               if(op[0] == 'Q'){
                   int x,y,k;
                   scanf("%d%d%d",&x,&y,&k);
                   x ^= ans; y ^= ans; k ^= ans;
                   ans = ScapeGoatTree::query(x,y,k);
                   printf("%d\n",ans);
               }
               else if(op[0] == 'M'){
                   int x,val;
                   scanf("%d%d",&x,&val);
                   x ^= ans; val ^= ans;
                   ScapeGoatTree::Modify(ScapeGoatTree::root,x,val);
               }
               else if(op[0] == 'I'){
                   int x,val;
                   scanf("%d%d",&x,&val);
                   x ^= ans; val ^= ans;
                   ScapeGoatTree::insert(x,val);
               }
          }
      }
      return 0;
  }
