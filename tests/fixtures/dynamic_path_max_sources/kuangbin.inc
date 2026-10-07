const int MAXN = 300010;
const int INF = 0x3f3f3f3f;
struct Node *null;
struct Node{
Node *fa,*ch[2];
int Max,val;
int rev;//旋转标记
int add;
inline void clear(int _val){
fa = ch[0] = ch[1] = null;
val = Max = _val;
rev = 0;
add = 0;
}
inline void push_up(){
Max = max(val,max(ch[0]->Max,ch[1]->Max));
}
inline void setc(Node *p,int d){
ch[d] = p;
p->fa = this;
}
inline bool d(){
return fa->ch[1] == this;
}
inline bool isroot(){
return fa == null || fa->ch[0] != this && fa->ch[1] != this ;
}
//翻转
inline void flip(){
if(this == null)return;
swap(ch[0],ch[1]);
rev ^= 1;
}
inline void update_add(int w){
if(this == null)return;
val += w;
add += w;
Max += w;
}
inline void push_down(){
if(rev){
ch[0]->flip(); ch[1]->flip(); rev = 0;
}
if(add){
ch[0]->update_add(add); ch[1]->update_add(add);
add = 0;
}
}
//直接标记下放
inline void go(){
if(!isroot())fa->go();
push_down();
}
inline void rot(){
Node *f = fa, *ff = fa->fa;
int c = d(), cc = fa->d();
f->setc(ch[!c],c);
this->setc(f,!c);
if(ff->ch[cc] == f)ff->setc(this,cc);
else this->fa = ff;
f->push_up();
}
inline Node* splay(){
go();
while(!isroot()){
if(!fa->isroot())
d()==fa->d() ? fa->rot() : rot();
rot();
}
push_up();
return this;
}
inline Node* access(){
for(Node *p = this,*q = null; p != null; q = p, p = p->fa){
p->splay()->setc(q,1);
p->push_up();
}
return splay();
}
//找该点的根
inline Node* find_root(){
Node *x;
for(x = access(); x->push_down(), x->ch[0] != null; x = x-> ch[0]);
return x;
}
//变为树根 (换根操作)
void make_root(){
access()->flip();
}
//切断该点和父亲结点的边
void cut(){
access();
ch[0]->fa = null;
ch[0] = null;
push_up();
}
//切断该点以 x 为根时, 该点和父亲结点的根
//要求这个点和 x 在同一颗树而且不能相同
//x 变为所在树的树根
void cut(Node* x){
if(this == x || find_root() != x->find_root())
puts("-1");
else {
x->make_root();
cut();
}
}
//该点连接到 x
//假如是有虚边信息的，需要先 x->access() 再连接
void link(Node *x){
if(find_root() == x->find_root())
puts("-1");
else {
make_root(); fa = x;
}
}
};
Node pool[MAXN],*tail;
Node *node[MAXN];
struct Edge{
int to,next;
}edge[MAXN*2];
int head[MAXN],tot;
inline void addedge(int u,int v){
edge[tot].to = v;
edge[tot].next = head[u];
head[u] = tot++;
}
void dfs(int u,int pre){
for(int i = head[u];i != -1;i = edge[i].next){
int v = edge[i].to;
if(v == pre)continue;
node[v]->fa = node[u];
dfs(v,u);
}
}
void ADD(Node *x,Node *y,int w){
x->access();
for(x = null; y != null; x = y, y = y->fa){
y->splay();
if(y->fa == null){
y->ch[1]->update_add(w);
x->update_add(w);
y->val += w;
y->push_up();
return;
}
y->setc(x,1);
y->push_up();
}
}
int ask(Node *x,Node *y){
x->access();
for(x = null; y != null; x = y, y = y->fa){
y->splay();
if(y->fa == null)
return max(y->val,max(y->ch[1]->Max,x->Max));
y->setc(x,1);
y->push_up();
}
}
int main()
{
int n;
while(scanf("%d",&n) == 1){
for(int i = 1;i <= n;i++)head[i] = -1;
tot = 0;
int u,v;
for(int i = 1;i < n;i++){
scanf("%d%d",&u,&v);
addedge(u,v);
addedge(v,u);
}
tail = pool;
null = tail++;
null->clear(-INF);
for(int i = 1;i <= n;i++){
node[i] = tail++;
scanf("%d",&v);
node[i]->clear(v);
}
dfs(1,1);
int m,op;
int x,y,w;
scanf("%d",&m);
while(m--){
scanf("%d",&op);
if(op == 1){
scanf("%d%d",&x,&y);
node[x]->link(node[y]);
}
else if(op == 2){
scanf("%d%d",&x,&y);
node[y]->cut(node[x]);
}
else if(op == 3){
scanf("%d%d%d",&w,&x,&y);
if(node[x]->find_root() != node[y]->find_root())
printf("-1\n");
else ADD(node[x],node[y],w);
}
else{
scanf("%d%d",&x,&y);
if(node[x]->find_root() != node[y]->find_root())
printf("-1\n");
else printf("%d\n",ask(node[x],node[y]));
}
}
printf("\n");
}
return 0;
}
