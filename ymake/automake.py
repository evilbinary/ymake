# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
from .function import toolchain,add_buildin,node_start,set_toolset,\
    set_kind,node_current,shell,node_set,cmd,get_config,node_get_parent
import os

def build(tool,target,opt={}):
    print('{} build {}'.format(tool.get('name'),target.get('name')))

    automake=target.get('build-tool')
    sourcedir=target.get('sourcedir')
    args=automake.get('configure')
    jobnum= node_get_parent(automake,'jobnum')

    try:
        shell(tool.get('configure'),args,cwd=sourcedir)
        
    except Exception as e:
        print('build error',e)
        pass

    shell(tool.get('make'),['-j'+str(jobnum)],cwd=sourcedir)

    
    pass
    
def automake(name=None, **kwargs):
    cur=node_current()
    if name==None:
        name=cur.get('name')
    node={
        'name': name,
        'type':'automake',
        'toolchain':'automake'
    }
    node.update(kwargs)
    if cur:
        cur['build-tool']=node    
    node_start(node)

def automake_end():
    cur=node_current()
    if cur and cur.get('type')=='automake':
        node_end()

def configure(*args):
    node_set('configure',list(args))


def init():
    toolchain('automake',build=build)
    set_kind("standalone")

    set_toolset("configure","./configure")
    set_toolset("automake","automake")
    set_toolset("autoconf","autoconf")
    set_toolset("libtool","libtool")
    set_toolset("pkg-config","pkg-config")
    set_toolset("make","make")

    add_buildin('automake',automake)
    add_buildin('configure',configure)

