# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
from .log import log
import inspect

nodes=[]

node_stack=[]


def node_start(n):
    cur=node_current()
    if cur:
        # print('n type',n.get('type'),'====',cur.get('type'),'=>',n.get('type')==cur.get('type') )
        if n.get('type')==cur.get('type'):
            node_del=node_stack.pop()
            nodes.append(node_del)
        n['parent']=cur
    node_stack.append(n)

    log.debug('{} {}'.format(n.get('type'),n.get('name')))
     
def node_end():
    if len(node_stack)>0:
        n=node_stack.pop()
        nodes.append(n)

def node_current():
    if len(node_stack)>0:
        return node_stack[-1]
    else:
        return None

def node_set(key,value):
    n=node_current()
    n[key]=value

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
        if n.get(key):
            return n.get(key)
        n=n.get('parent')
    return None

def node_get_parent_all(n,key):
    ret=[]
    while n:
        if n.get(key):
            if isinstance( n.get(key),str):
                ret.append(key)
            else:
                ret+=n.get(key)                
        n=n.get('parent')
    return ret

def node_update(data):
    n=node_current()
    return n.update(data)

def node_extend(key,value):
    n=node_current()
    if not n.get(key):
        
        caller_frame = inspect.currentframe().f_back
        caller_file_path = inspect.getframeinfo(caller_frame)
        # print('call==>',caller_file_path)        
        # print('get=>',value,'==>',list(value) )
        n[key]=list(value)
        return value
    # print('get1=>',value)
    n[key].extend(value)

def node_len():
    return len(nodes)+len(node_stack)

def nodes_get_type_and_name(ty,name):
    for n in nodes:
        if n.get('type')== ty and n.get('name')==name :
            return n
    for n in node_stack:
        if n.get('type')== ty and n.get('name')==name :
            return n
    return None