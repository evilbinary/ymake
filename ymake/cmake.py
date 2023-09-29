# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
from function import toolchain,add_buildin,node_start,set_toolset,set_kind

def build(tool,target,opt={}):
    print('cmake build',tool)
    pass
    
def cmake(name, **kwargs):
    node={
        'name': name,
        'type':'cmake',
        'toolchain':'cmake'
    }
    node.update(kwargs)
    node_start(node)

def cmake_end():
    cur=node_current()
    if cur and cur.get('type')=='cmake':
        node_end()

def init():
    toolchain('cmake',build=build)
    set_kind("standalone")
    #set toolset
    set_toolset("cmake","cmake")

    add_buildin('cmake',cmake)