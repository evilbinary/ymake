# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
from log import log
import os
import inspect

nodes=[]

node_stack=[]


node_level={
    'project':0,
    'target':1,
    'rule':1,
    'toolchain':1,
    'option':1
}

def node_set_level(k,v):
    node_level[k]=v

def get_format(str,data):
    try:
        return str.format(**data)
    except Exception as e:
        log.warn('get format {} {} {}'.format(str,e,data))
        return str

def get_formats(l,data):
    ret=[]
    for i in l:
        new=get_format(i,data)
        ret.append(new)
    return ret

def get_target_data(target):
    data={}
    target_name=node_get_parent(target,'name')
    target_plat=node_get_parent(target,'plat')
    target_mode=node_get_parent(target,'mode')
    target_arch=node_get_parent(target,'arch')
    target_build_dir=node_get_parent(target,'build-dir')

    data['name']=target_name
    data['plat']=target_plat
    data['mode']=target_mode
    data['arch']=target_arch

    target_build_dir=get_format(target_build_dir,data)

    data['buildir']=target_build_dir
    return data

def format_target_var(target,var):
    data=get_target_data(target)
    return get_format(var,data)


def node_get_formated(target,key):
    build_dir=target.get(key)
    if not build_dir:
        if target.get('project'):
            build_dir=target.get('project').get(key)

    if not build_dir:
        return None
    build_dir=format_target_var(target,build_dir)
    # print(target.get('name'),'build dir=',build_dir)

    build_dir=os.path.normpath(build_dir)

    return build_dir


def get_list_args(args):
    ret=[]
    for a in args:
        if isinstance(a,str):
            s=a.split(' ')
            if len(s)>0:
                ret+=[x for x in s if x != '']
            else:
                ret.append(a.strip())
        else:
            ret+=a
    return ret

class Node(dict):
    
    # obj={}
    # def __init__(self,val,**vals):
    #     self.obj.update(val)
    #     super(val)

    # def update(self,vals):
    #     self.obj.update(vals)
    def name(self):
        return self.get('name')

    def targetfile(self):
        build_dir=node_get_formated(self,'build-dir')
        name=self.get('name')
        if self.get('filename'):
            name= self.get('filename')
        if build_dir:
            return build_dir+'/'+name
        else:
            return None

    def sourcefiles(self):
        files=self.get('files')
        ret=[]
        for file in files:
            file=format_target_var(self,file)
            ret.append(file)
        return ret

    def objectfiles(self):
        return self.get('file-objs')

    def set(self,key,val):
        self[key]=val

    def toolchain(self):
        toolchain_name=  self.get('toolchain')
        if not toolchain_name:
            toolchain_name = node_get_parent(self,'toolchain')
        toolchain=nodes_get_type_and_name('toolchain',toolchain_name)
        
        return toolchain

    def tool(self,tool):
        toolchain_name= node_get_parent(self,'toolchain')

        toolchain=nodes_get_type_and_name('toolchain',toolchain_name)
        if toolchain:
            return toolchain.get(tool)
        return None

    def get(self,key):
        if key in['arch_type','arch' ]:
            return node_get_parent(self,key)
        if key in self:
            return self[key]
        return None

    def get_arch(self):
        return self.get('arch')

    def arch(self):
        return self.get('arch')

    def arch_type(self):
        return self.get('arch_type')

    def get_arch_type(self):
        return self.get('arch_type')

    def add(self,key,*val,**kwargs):
        after=kwargs.pop('after',False)
        vals=get_list_args(val)
  
        node_op_extend(self,key,vals,after,True)

    def plat(self):
        return node_get_parent(self,'plat')

    def get_config(self,key):
        return node_get_parent(self,key)

def is_same_level(n1,n2):
    if node_level.get(n1.get('type'))== node_level.get(n2.get('type')):
        return True
    return False

def node_start(n):
    cur=node_current()
    if cur:
        # print('n type',n.get('type'),'====',cur.get('type'),'=>',n.get('type')==cur.get('type') )
        if is_same_level(n,cur):
            node_del=node_stack.pop()
            nodes_append(node_del)
        n['parent']=cur
    node_stack.append(n)

    log.debug('{} {}'.format(n.get('type'),n.get('name')))
     
def node_end():
    if len(node_stack)>0:
        n=node_stack.pop()
        nodes_append(n)
        # nodes.append(n)

def node_save():
    n =node_current()
    node_stack.append(n)

def node_restore():
    node_end()

def node_current():
    if len(node_stack)>0:
        return node_stack[-1]
    else:
        return None

def node_set(key,value):
    n=node_current()
    if n:
        n[key]=value
    else:
        log.warn('node current is null')

def node_get(key):
    n=node_current()
    return n.get(key)

def node_get_all(key):
    n =node_current()
    while n:
        if n.get(key):
            return n.get(key)
        n=n.get('parent')
    return None

def node_get_parent(n,key):
    while n:
        if key in n:
            if n[key]:
                return n[key]
        n=n.get('parent')
    return None

def node_get_parent_all(n,key):
    ret=[]
    while n:
        if n.get(key):
            if isinstance( n.get(key),str):
                ret.append(key)
            else:
                # print('+====ret=',ret,'==>',n.get(key))
                ret+=n.get(key)                
        n=n.get('parent')
    return ret

def node_update(data):
    n=node_current()
    return n.update(data)

def node_extend(key,value,t=1):
    n=node_current()
    return node_op_extend(n,key,value,t)

def node_op_extend(n,key,value,tail=True,nodup=False):
    if not n.get(key):       
        # caller_frame = inspect.currentframe().f_back
        # caller_file_path = inspect.getframeinfo(caller_frame)
        # print('call==>',caller_file_path)        
        # print('get=>',value,'==>',list(value) )
        if isinstance(value,list):
            n[key]=list(set(value))
        elif isinstance(value,tuple):
            n[key]=list(value)
        else:
            n[key]=[value]
        return value
    if nodup:
        # value=list(set(value))
        value= list(sorted(set(value), key=value.index))

    if tail:
        n[key].extend(value)
    else:
        n[key][:0]=value
    if nodup:
        n[key]=list(sorted(set(n[key]), key=n[key].index))
        # n[key]=list(set(n[key]))
    
    # print('get1=>',n.get(key),'==',value)

def node_len():
    return len(nodes)+len(node_stack)


def node_finish():
    global nodes
    # for s in node_stack:
    #     nodes_append(s)
    nodes.extend(node_stack)
    node_stack.clear()
    all_nodes=nodes_merge(nodes)
    nodes.clear()
    nodes+=all_nodes

def nodes_merge(nodes):
    unique_list = []
    seen_names = set()

    for n in nodes:
        name = n.get('name')+n.get('type')
        if name not in seen_names:
            seen_names.add(name)
            unique_list.append(n)
    return unique_list

def nodes_append(n):
    dup=False
    for nn in nodes:
        if n.get('name')==nn.get('name') and n.get('type')== nn.get('type'):
            dup=True
            break
    if not dup:
        nodes.append(n)
    # else:
    #     log.error('dup {}'.format(n.get('name') ))

def nodes_get_type_and_name(ty,name):
    for n in nodes:
        if n.get('type')== ty and n.get('name')==name :
            return n
    for n in node_stack:
        if n.get('type')== ty and n.get('name')==name :
            return n
    return None

def nodes_get_all_type(ty):
    ret=[]
    for n in nodes:
        if n.get('type')== ty:
            ret.append(n)
    for n in node_stack:
        if n.get('type')== ty:
            ret.append(n)
    return ret