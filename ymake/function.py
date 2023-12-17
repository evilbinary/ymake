# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
from node import *
from log import log
from colorama import Fore, Back, Style, init
import os
import glob
import importlib
import importlib.util
import re
import math
import platform 
import sys
import json
import networkx as nx
import fnmatch
import types
import argparse
import inspect
import hashlib
import datetime
from op import mod_os,mod_path,mod_string,cmd,shell,mod_io,mod_math
from globa import mode,cache
from pathlib import Path
from diskcache import Cache


buildin_module={}

def project(name, **kwargs):
    targets = kwargs.pop('targets', [])
    node = {
        'name': name,
        'type':'project',
        'version': kwargs.pop('version',''),
        'desc': kwargs.pop('desc',''),
        'targets': targets,
        'target-objs': {},
        'toolchain':'gcc',
        'build-dir':'build/{plat}/{arch}/{mode}',
        'build-obj-dir':'build/{plat}/{arch}/{mode}/objs/',
        'cache-dir':'.cache',
        'arch':'',
        'plat':'',
        'mode': '',
        'arch_type':''
    }
    node.update(kwargs)
    node_start(node)

    if not os.path.exists(node.get('cache-dir')):
        os.mkdir(node.get('cache-dir'))
    global cache
    cache=Cache(node.get('cache-dir'))
    node['cache']=cache
    
        

def target(name, **kwargs):
    caller_frame = inspect.currentframe().f_back
    caller_file_path = inspect.getframeinfo(caller_frame).filename
    simplified_path = os.path.normpath(caller_file_path)
    dir_name=os.path.dirname(simplified_path)

    relative_dir_name=os.path.relpath(dir_name)
    if relative_dir_name.startswith('..'):
        relative_dir_name='/'.join(relative_dir_name.split(os.sep)[2:])

    log.debug('relpath {}'.format(relative_dir_name))

    parent=node_current()
    while parent:
        if parent.get('type')=='project':
            break
        node_end()
        parent=node_current()
    node = Node({
        'name': name,
        'type':'target',
        'kind': 'binary',
        'deps': [],
        'files': [],
        'file-objs':[],
        'cflags':[],
        'file-path': relative_dir_name,
        'project': parent,
        'includedirs':[],
        'file-includedirs':[],
    })

    node.update(kwargs)


    # def targetfile():
    #     return node.get('name')

    # node['targetfile']=targetfile

    if parent:
        # print('add target',name,' parent:',parent.get('type'),parent.get('name') )
        # print('add target parent === cur',parent.get('type')=='project')
        if parent.get('type')=='project':
            parent['targets'].append(name)
            parent['target-objs'][name]=node
        elif parent.get('type')==node.get('type'):
            pass
        else:
            log.error('target {} not append after project cur is {} {}'
            .format(name,
                parent.get('type'),
                parent.get('name')
            ))


    node_start(node)

    files = kwargs.pop('files', [])
    if len(files)>0:
        add_files(files[0])

def toolchain(name, **kwargs):
    prefix=kwargs.pop('prefix','')
    node = {
        'name': name,
        'type':'toolchain',
        'cc': prefix+'gcc',
        'cxx': prefix+'c++',
        'ld': prefix+'ld',
        'ar': prefix+'ar',
        'as': prefix+'as',
        'objcopy': prefix+'objcopy',
        'sh': prefix+'gcc',
        'ranlib': prefix+'ranlib',
        'is_modify': is_file_modified,
        'prefix': prefix,
    }
    node.update(kwargs)
    node_start(node)

def option(name,**kwargs):
    node=nodes_get_type_and_name('option',name)
    if not node:
        node={
            'name': name,
            'type':'option',
            'description':'',
            'default': False,
            'showmenu':False,
        }
        node.update(kwargs)
        node_start(node)
    else:
        node.update(kwargs)
        node_start(node)
        node['parent']=None

def root(name, **kwargs):
    node={
        'name': name,
        'type':'root',
    }
    node.update(kwargs)
    node_start(node)


def rule(name, **kwargs):
    node = {
        'name': name,
        'type':'rule',
    }
    node.update(kwargs)
    node_start(node)

def add_rules(*rule_name):
    rule_name=get_list_args(rule_name)
    node_extend('rules',rule_name)

def set_toolset(k,v):
    node_set(k,v)

def set_extensions(*exts):
    exts=get_list_args(exts)
    node_extend('extensions',exts)

def on_build_file(fn):
    cur=node_current()
    node_extend('on_build_file',fn)

def on_build(fn):
    cur=node_current()
    node_extend('on_build',fn)

def on_run(fn):
    cur=node_current()
    node_extend('on_run',fn)

def after_build(fn):
    cur=node_current()
    node_extend('after_build',fn)

def after_link(fn):
    cur=node_current()
    node_extend('after_link',fn)

def after_clean(fn):
    cur=node_current()
    node_extend('after_clean',fn)

def before_build(fn):
    cur=node_current()
    node_extend('before_build',fn)

def before_run(fn):
    cur=node_current()
    node_extend('before_run',fn)

def on_config(fn):
    cur=node_current()
    node_extend('on_config',fn)


def on_load(fn):
    cur=node_current()
    node_extend('on_load',fn)

def set_default(t):
    cur=node_current()
    node_set('default',t)
    if None==cur.get('value'):
        cur['value']=t
        
def set_showmenu(t):
    node_set('showmenu',t)

def set_description(t):
    node_set('description',t)


def set_configdir(d):
    node_set('configdir',d)

def set_configvar(key,val):
    configvar=node_get('configvar')
    if not configvar:
        configvar={}
    configvar[key]=val
    node_set('configvar',configvar)

def add_configfiles(file,prefixdir=None):
    node_extend('configfiles',[file])


def add_kind(kind):
    node_set('kind',kind)

def set_kind(kind):
    node_set('kind',kind)

def set_toolchain(tool):
    node_set('toolchain',tool)

def set_toolchains(tool):
    set_toolchain(tool)


def add_files(*files,rules=None):

    cur=node_current()
    dir_name=cur['file-path']  

    files=get_list_args(files)

    node_extend('files',files)

    files=[format_target_var(cur,item) for item in files ]
    node_set('file-rules',rules)
    # match_files=file_match(files,dir_name)
    
    #log.debug('{} {} add files match {} => {} pwd: {}'.format(cur.get('type'),cur.get('name') ,files,match_files,os.getcwd() ))
    #cur['file-objs'].extend(match_files)

def get_build_dir():
    cur=node_current()
    return node_get_parent(cur,'build-dir')

def get_build_obj_dir():
    cur=node_current()
    build_obj_dir=node_get_parent(cur,'build-obj-dir')
    return build_obj_dir

def add_deps(*deps):
    deps=get_list_args(deps)
    node_extend('deps',deps)

def add_packages(*deps):
    deps=get_list_args(deps)
    node_extend('deps',deps)

def script_dir():
    caller_frame = inspect.currentframe().f_back
    caller_file_path = inspect.getframeinfo(caller_frame).filename
    simplified_path = os.path.normpath(caller_file_path)
    dir_name=os.path.dirname(simplified_path)
    return dir_name

def file_match(patterns,root='.'):
    matches=[]
    if isinstance(patterns,str):
        pp=patterns
        # p=os.path.join(root,pp)
        p=os.path.normpath(pp)

        matches=glob.glob(p)

        log.debug('str root=>{} patterns=>{} p=>{} matches=>{}'.format(root,pp,p,matches))

    elif isinstance(patterns,list) or isinstance(patterns,tuple):
        for pp in patterns:
            p1=os.path.join(root,pp)
            p=os.path.normpath(p1)
            g=glob.glob(p)
            if len(g)==0:
                # for i in Path(root).glob(pp):
                #    matches.append(str(i)) 
                pass
            else:
                matches+= g
            log.debug('root=>{} patterns=>{} p=>{} matches=>{}'.format(root,pp,p,matches))

    else:
        log.error('pattherns type error {}'.format(type(patterns)) )
    return matches


def add_includedirs(*path,public=False):
    path=get_list_args(path)
    log.debug('add includedirs {}'.format(path))
    cur=node_current()
    if not cur:
        log.warn('not found cur node')
        return
    cur['includedirs']= path
    
    dir_name=cur['file-path'] 

    include_dirs=[format_target_var(cur,item) for item in path ]

    log.debug('add includedirs var {}'.format(include_dirs))

    match_files=file_match(include_dirs,dir_name)
    log.debug('add includedirs match {} => {} pwd: {}'.format(include_dirs,match_files,os.getcwd() ))

    cur['file-includedirs'].extend(match_files)

def add_defines(*path):
    path=get_list_args(path)
    node_extend('defines',path)
    pass

def add_cflags(*cflags,**kwargs):
    cflags=get_list_args(cflags)
    node_extend('cflags',cflags)

def add_cxxflags(*cflags,**kwargs):
    cflags=get_list_args(cflags)
    node_extend('cxxflags',cflags)
    pass

def add_ldflags(*ldflags,**kwargs):
    before=kwargs.pop('before',True)

    ldflags=get_list_args(ldflags)
    cur=node_current()
    ldflags=[format_target_var(cur,item) for item in ldflags ]
    # print('============>ldflags',ldflags)

    node_extend('ldflags',ldflags,0)

def add_toolchain_dirs(*path):
    node_extend('toolchain-dir',path)

def get_toolchain_dirs():
    n=node_current()
    return node_get_parent_all(n,'toolchain-dir')

def get_toolchain():
    n=node_current()
    tool=node_get_parent(n,'toolchain')
    return tool

def set_sourcedir(dir):
    node_set('sourcedir',dir)

def has_cflags(*cflags):
    for flag in cflags:
        node_get('cflags')==flag
        return True
    return False

def get_cflags():
    #return node_get('cflags')
    flags=[]
    n=node_current()
    flags+=node_get_parent_all(n,'cflags')
    # print('=============>',node_get_parent_all(target,'cflags'))

    defined=node_get_parent_all(n,'defines')
    if defined:
        flags+=['-D'+item for item in defined]

    return flags

def get_arch():
    return node_get_all('arch')

def set_arch(arch):
    node_set('arch',arch)

def set_defaultplat(plat):
    node_set('plat',plat)

def get_archs():
    return node_get('arch')

def set_archs(arch):
    node_set('archs',arch)

def set_arch_type(arch):
    node_set('arch_type',arch)

def get_arch_type():
    arch_type= node_get_all('arch_type')
    return arch_type

def get_system():
    sys= node_get('system')
    return sys

def set_config(key,val,*rest):
    if len(rest)==0:
        node_set(key,val)
    else:
        merged_list = []
        if isinstance(val,str):
            merged_list.append(val.strip())
        else:
            merged_list.extend(val)
        for sublist in rest:
            merged_list.extend(sublist)
        node_set(key,merged_list)

def is_mode(m):
    val=get_config('mode')
    if val ==m:
        return True
    return False

def get_config(key):
    cur=node_current()
    if not cur:
        p=nodes_get_all_type('project')
        if len(p)>0:
            cur=p[0]
    val= node_get_parent(cur,key)
    return val

def is_plat(*patterns):
    platform=get_plat()
    matches = []
    for pattern in patterns:
        regex_pattern = pattern.replace('*', '.*')  # 将模式中的 * 替换为正则表达式中的 .*
        match = re.match(regex_pattern, platform)
        matches.append(bool(match))
    return matches

def toolchain_end():
    cur=node_current()
    if cur and cur.get('type')=='toolchain':
        node_end()

def project_end():
    cur=node_current()
    if cur and cur.get('type')=='project':
        node_end()

def target_end():
    cur=node_current()
    if cur and cur.get('type')=='target':
        node_end()

def rule_end():
    cur=node_current()
    if cur and cur.get('type')=='rule':
        node_end()

def option_end():
    cur=node_current()
    if cur and cur.get('type')=='option':
        node_end()

def has_config(*names):
    count=0
    for name in names:
        ret=nodes_get_type_and_name('option',name)
        if ret and ret.get('value'):
            count+=1
    if count==len(names):
        return True
    return False

def get_plat():
    cur=node_current()
    plat= node_get_parent(cur,'plat')
    return plat

def set_filename(file):
    node_set('filename',file)

def add_subs(*path):
    caller_frame = inspect.currentframe().f_back
    caller_file_path = inspect.getframeinfo(caller_frame).filename
    simplified_path = './'+caller_file_path
    if caller_file_path.startswith('/'):
        simplified_path = caller_file_path

    dir_name=os.path.dirname(simplified_path)

    # print('caller_file_path=>',caller_file_path)
    # print('simplified_path=>',simplified_path)

    # print('dir_name=>',dir_name)

    relative_dir_name=os.path.relpath(dir_name)
    log.debug('add subs {} relpath {}'.format(dir_name,relative_dir_name ))    
    paths= file_match(path,dir_name)
    for p in paths:
        try:
            node_save()
            import_source(p)
            node_restore()
        except FileNotFoundError:
            print('file not found ',p)
        except ImportError as e:
            print('warn not found file',p)
            e.with_traceback()
        except Exception as e:
            print('error import file',p,e)
            e.with_traceback()

    # node_end()
    pass

includes=add_subs


def is_file_modified(source_file,target_file):
    # md5_before = hashlib.md5(open(source_file).read()).hexdigest()
    try:
        source_modified = os.path.getmtime(source_file)
        output_modified = os.path.getmtime(target_file)
        if source_file==target_file:
            out_time= cache.get('mtime:'+target_file,default=0)
            if out_time< output_modified:
                output_modified=out_time

            cache.set('mtime:'+target_file,source_modified)

        # print('source_file=>',source_file,'target_file->',target_file)
        # print('source_modified=>',source_modified,'output_modified->',output_modified,'is modify=>',source_modified > output_modified)
        return source_modified > output_modified
    except:
        return True

def get_include(target,path=''):
    includedirs=list(target.get('file-includedirs'))
    log.debug('include dirs=>{}'.format(includedirs))
    includedirs=['-I' + os.path.join(path,item) for item in includedirs]
    return includedirs

def get_includedirs(target,path=''):
    includedirs=list(target.get('includedirs'))
    log.debug('includedirs=>{}'.format(includedirs))
    return includedirs

def is_host(*name):
    name=list(name)
    if 'mac' in name:
        name+=['darwin']

    if platform.system().lower() in name:
        return True
    return False

def cprint(text):
    colors = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'reset': '\033[0m'
    }

    for color in colors:
        placeholder = f'${{{color}}}'
        if placeholder in text:
            text = text.replace(placeholder, colors[color])

    text = text.replace('${clear}', colors['reset'])
    print(text)

def check_module(module_name):
    module_spec = importlib.util.find_spec(module_name)
    if module_spec is None:
        print('moudle: {} not found'.format(module_name))
        return None
    else:
        print('moudle: {} can be imported!'.format(module_name))
        return module_spec

def import_module_from_spec(module_spec):
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module

def import_source(file):
    dir_name=os.path.dirname(file)
    base_name=os.path.basename(file)

    module_name = dir_name+"."+base_name

    module_spec = importlib.util.spec_from_file_location(module_name, file)
    module = importlib.util.module_from_spec(module_spec)

    # for node
    module.target=target
    module.rule=rule
    module.project=project

    module.rule_end=rule_end
    module.project_end=project_end
    module.toolchain_end=toolchain_end

    module.option=option
    module.option_end=option_end
    module.set_showmenu=set_showmenu
    module.set_description=set_description



    module.true=True
    module.false=False

    # module.target=target
    module.add_kind=add_kind
    module.set_kind=set_kind
    module.add_files=add_files
    module.add_deps =add_deps
    module.add_subs= add_subs
    module.includes= includes
    module.add_includedirs= add_includedirs
    module.add_defines= add_defines
    module.get_arch=get_arch
    module.get_archs=get_archs
    module.get_plat=get_plat
    module.get_arch_type=get_arch_type

    #for project
    module.set_defaultplat=set_defaultplat
    module.set_toolchain=set_toolchain

    module.is_plat=is_plat
    module.is_mode=is_mode
    module.set_toolchains=set_toolchains
    module.set_arch_type=set_arch_type
    module.set_arch=set_arch

    module.set_config=set_config
    module.get_config=get_config
    module.add_cflags=add_cflags
    module.add_cxxflags=add_cxxflags
    module.add_ldflags=add_ldflags

    module.add_rules=add_rules

    module.set_extensions=set_extensions
    module.set_configdir=set_configdir
    module.set_configvar=set_configvar
    module.add_configfiles=add_configfiles
    module.set_default= set_default

    module.has_config=has_config
    module.get_toolchain=get_toolchain
    module.set_sourcedir=set_sourcedir
    module.get_cflags=get_cflags
    module.add_packages=add_packages
    module.set_filename=set_filename


    module.on_build=on_build
    module.on_build_file=on_build_file
    module.on_run= on_run
    module.after_build=after_build
    module.before_run=before_run
    module.on_load=on_load
    module.add_buildin=add_buildin
    module.before_build=before_build
    module.after_link=after_link
    module.after_clean=after_clean
    module.on_config=on_config

    module.get_build_dir=get_build_dir
    module.get_build_obj_dir = get_build_obj_dir


    #op function
    module.os=mod_os
    module.path=mod_path
    module.string=mod_string
    module.io=mod_io
    module.math= mod_math

    #utils
    module.cmd=cmd
    module.shell=shell
    module.cprint=cprint
    module.is_host=is_host

    for k in buildin_module:
        setattr(module,k,buildin_module.get(k))

    
    module_spec.loader.exec_module(module)

    return module

def add_buildin(key,val,level=1):
    buildin_module[key]=val
    node_set_level(key,level)

def print_progress(type,progress,total_nodes,node,opt=None):
    if opt:
        print("{}[{:.0f}.{:.0f}%]:{} {}{} target {}{}"
            .format( Fore.GREEN,opt.get('progress')/opt.get('total_nodes')*100,progress/total_nodes*100,type,Style.RESET_ALL,Fore.MAGENTA,node,Style.RESET_ALL)
        )
    else:
        print("{}[{:.0f}%]:{} {}{} target {}{}"
            .format( Fore.GREEN,progress/total_nodes*100 ,type,Style.RESET_ALL,Fore.MAGENTA,node,Style.RESET_ALL)
        )


