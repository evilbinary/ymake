# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
from .node import *
from .log import log
from colorama import Fore, Back, Style, init
import os
import glob

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
        'mode':'release',
        'arch_type':''
    }
    node.update(kwargs)
    node_start(node)

    if not os.path.exists(node.get('cache-dir')):
        os.mkdir(node.get('cache-dir'))

def target(name, **kwargs):
    caller_frame = inspect.currentframe().f_back
    caller_file_path = inspect.getframeinfo(caller_frame).filename
    simplified_path = os.path.normpath(caller_file_path)
    dir_name=os.path.dirname(simplified_path)

    relative_dir_name=os.path.relpath(dir_name)
    log.debug('relpath {}'.format(os.path.relpath(dir_name)))

    parent=node_current()
    while parent:
        if parent.get('type')=='project':
            break
        node_end()
        parent=node_current()

    node = {
        'name': name,
        'type':'target',
        'kind': '',
        'deps': [],
        'files': [],
        'file-objs':[],
        'cflags':[],
        'file-path': relative_dir_name,
        'project': parent,
        'includedirs':[],
        'file-includedirs':[]
    }
    node.update(kwargs)

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
        'is_modify': is_file_modified
    }
    node.update(kwargs)
    node_start(node)


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



def set_extensions(*exts):
    exts=get_list_args(exts)
    node_extend('extensions',exts)

def on_build_file(fn):
    cur=node_current()
    node_set('on_build_file',fn)

def on_build(fn):
    cur=node_current()
    node_set('on_build',fn)

def set_configdir(d):
    node_set('configdir',d)

def set_configvar(*var):
    var=get_list_args(var)
    node_set('configvar',var)

def add_configfiles(file,prefixdir=None):
    node_extend('configfiles',file)


def add_kind(kind):
    node_set('kind',kind)

def set_kind(kind):
    node_set('kind',kind)

def set_toolchain(tool):
    node_set('toolchain',tool)

def set_toolchains(tool):
    set_toolchain(tool)


def get_list_args(args):
    ret=[]
    for a in args:
        if isinstance(a,str):
            ret.append(a)
        else:
            ret+=a
    return ret

def add_files(*files,rules=None):
    node_extend('files',files)
    cur=node_current()
    dir_name=cur['file-path']  

    files=get_list_args(files)

    files=[format_target_var(cur,item) for item in files ]

    match_files=file_match(files,dir_name)
    
    log.debug('{} {} add files match {} => {} pwd: {}'.format(cur.get('type'),cur.get('name') ,files,match_files,os.getcwd() ))
    cur['file-objs'].extend(match_files)
    

def add_deps(*deps):
    cur=node_current()
    cur['deps'].extend(deps)

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
            p=os.path.join(root,pp)
            p=os.path.normpath(p)
            
            matches+= glob.glob(p)
            log.debug('root=>{} patterns=>{} p=>{} matches=>{}'.format(root,pp,p,matches))

    else:
        log.error('pattherns type error {}'.format(type(patterns)) )
    return matches



def scriptdir():
    caller_frame = inspect.currentframe().f_back
    caller_file_path = inspect.getframeinfo(caller_frame).filename
    simplified_path = os.path.normpath(caller_file_path)
    dir_name=os.path.dirname(simplified_path)
    return dir_name

def path_join(a,b):
    ret=os.path.join(a,b)

    ret=os.path.normpath(ret)

    return ret


def get_fromat(str,data):
    try:
        return str.format(**data)
    except Exception as e:
        return str

def get_fromats(l,data):
    ret=[]
    for i in l:
        new=get_fromat(i,data)
        ret.append(new)
    return ret

def format_target_var(target,var):
    target_name=node_get_parent(target,'name')
    target_plat=node_get_parent(target,'plat')
    target_mode=node_get_parent(target,'mode')
    target_arch=node_get_parent(target,'arch')
    data={}
    data['name']=target_name
    data['plat']=target_plat
    data['mode']=target_mode
    data['arch']=target_arch
    return get_fromat(var,data)

def add_includedirs(*path,public=False):
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
    node_extend('defines',path)
    pass

def add_cflags(*cflags):
    cflags=get_list_args(cflags)
    node_extend('cflags',cflags)

def add_cxxflags(*cflags):
    cflags=get_list_args(cflags)
    node_extend('cxxflags',cflags)
    pass

def add_ldflags(*ldflags,force=False):
    ldflags=get_list_args(ldflags)
    cur=node_current()

    ldflags=[format_target_var(cur,item) for item in ldflags ]
    # print('============>ldflags',ldflags)

    node_extend('ldflags',ldflags)

def has_cflags(*cflags):
    for flag in cflags:
        node_get('cflags')==flag
        return True
    return False

def get_cflags():
    return node_get('cflags')

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

def set_config(key,*val):
    val=get_list_args(val)
    node_set(key,val)

def get_config(key):
    cur=node_current()
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

def get_plat():
    cur=node_current()
    plat= node_get_parent(cur,'plat')
    return plat

def add_subs(*path):
    caller_frame = inspect.currentframe().f_back
    caller_file_path = inspect.getframeinfo(caller_frame).filename
    simplified_path = './'+caller_file_path
    dir_name=os.path.dirname(simplified_path)

    # print('caller_file_path=>',caller_file_path)
    # print('simplified_path=>',simplified_path)

    # print('dir_name=>',dir_name)

    relative_dir_name=os.path.relpath(dir_name)
    log.debug('add subs {} relpath {}'.format(dir_name,relative_dir_name ))

    paths= file_match(path,dir_name)
    for p in paths:
        try:
            import_source(p)
        except FileNotFoundError:
            print('file not found ',p)
        except ImportError as e:
            print('warn not found file',p)
            e.with_traceback()
        except Exception as e:
            print('error import file',p,e)
            e.with_traceback()
    
    pass


def is_file_modified(source_file,target_file):
    # md5_before = hashlib.md5(open(source_file).read()).hexdigest()
    try:
        source_modified = os.path.getmtime(source_file)
        output_modified = os.path.getmtime(target_file)
        
        # print('source_file=>',source_file,'target_file->',target_file)
        # print('source_modified=>',source_modified,'output_modified->',output_modified)
        return source_modified > output_modified
    except:
        return True


def shell(cmd,args,env=None):
    process=None
    if env:
        process = subprocess.Popen(cmds, shell=True, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        process = subprocess.Popen(cmds, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if process.returncode == 0:
        pass
    else:
        log.error(error.decode())
        raise Exception(error.decode())


def cmd(cmd,args,env=None):
    cmds = [cmd]+args
    log.debug('cmds =>{}'.format(cmds))

    print(' '.join(cmds))
    process=None
    if env:
        process = subprocess.Popen(cmds, shell=False, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        process = subprocess.Popen(cmds, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)    

    output, error = process.communicate()

    if process.returncode == 0:
        pass
    else:
        log.error(error.decode())
        raise Exception(error.decode())

def get_include(target):
    includedirs=list(target.get('file-includedirs'))
    log.debug('includedirs=>{}'.format(includedirs))

    includedirs=['-I' + item for item in includedirs]
    return includedirs


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

    # module.target=target
    module.add_kind=add_kind
    module.set_kind=set_kind
    module.add_files=add_files
    module.add_deps =add_deps
    module.add_subs= add_subs
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
    module.on_build=on_build
    module.on_build_file=on_build_file

    #op function

    mod_os = type("os", (), {})
    module.os=mod_os
    mod_os.scriptdir=scriptdir
    
    mod_path = type("path", (), {})
    module.path=mod_path
    mod_path.join=path_join


    #utils
    module.cmd=cmd
    module.shell=shell
    
    module_spec.loader.exec_module(module)

    return module


def print_progress(progress,total_nodes,node,opt=None):
    if opt:
        print("{}[{:.0f}%]:{} {}compile target {}{}"
            .format( Fore.GREEN,opt.get('progress')/opt.get('total_nodes')*100+progress/total_nodes*10 ,Style.RESET_ALL,Fore.MAGENTA,node,Style.RESET_ALL)
        )
    else:
        print("{}[{:.0f}%]:{} {}compile target {}{}"
            .format( Fore.GREEN,progress/total_nodes*100 ,Style.RESET_ALL,Fore.MAGENTA,node,Style.RESET_ALL)
        )
