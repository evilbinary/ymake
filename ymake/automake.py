# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
import os
from function import toolchain,add_buildin,node_start,set_toolset,\
    set_kind,node_current,shell,node_set,cmd,get_config,node_get_parent,\
    node_get_formated
from builder import get_build_target
from log import log

def build(tool,target,opt={}):
    log.debug('{} build {}'.format(tool.get('name'),target.get('name')))

    automake=target.get('build-tool')
    sourcedir=target.get('sourcedir')
    args=automake.get('configure')
    jobnum= node_get_parent(automake,'jobnum')
    build_dir=node_get_formated(target,'build-dir')

    build_dir_abs=os.path.abspath(build_dir)
    build_config_abs=os.path.abspath(os.path.join(sourcedir,tool.get('configure')))

    build_dir_target=os.path.join(build_dir_abs,target.get('name'))

    build_target=get_build_target(target,'/'+target.get('name')+'/lib',automake.get('name') )
    build_target_abs=os.path.abspath(build_target)


    log.debug('build_config_abs=>{}'.format(build_config_abs))
    log.debug('build_target_abs=>{}'.format(build_target_abs))

    is_modify_target=False
    if os.path.exists(build_target_abs):
        is_modify_target=True
        return

    if not os.path.exists(build_config_abs):
        shell('aclocal')
        shell('autoconf')
        shell('automake --add-missing')

    args+=['--prefix='+build_dir_target]
    try:
        shell(tool.get('configure'),args,cwd=sourcedir)
        
    except Exception as e:
        print('build error',e)
        pass

    shell(tool.get('make'),['install','-j'+str(jobnum)],cwd=sourcedir)

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

