# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
from .log import log
from .function import *


def get_build_dir(target,key):
    build_dir=target.get(key)
    if not build_dir:
        build_dir=target.get('project').get(key)

    build_dir=format_target_var(target,build_dir)
    # print(target.get('name'),'build dir=',build_dir)

    build_dir=os.path.normpath(build_dir)

    return build_dir


def get_build_target(target):
    build_dir=get_build_dir(target,'build-dir')
    ext=''
    prefix=''
    if target.get('kind')=='static':
        ext='.a'
        prefix='lib'
    elif target.get('kind')=='shared':
        ext='.so'
        prefix='lib'
    out_name=os.path.join(build_dir,prefix+target.get("name")+ext)
    # print('build target name ',out_name,build_dir,target.get("name"))
    return out_name

def get_object_name(obj,full=False):
    obj_file_name=obj
    if full:
        obj_file_name=obj
    parts = obj_file_name.rsplit('.c', 1)
    new_obj_name = '.o'.join(parts)
    return new_obj_name

def get_target_cflags(target):
        flags=[]
        if target.get('cflags'):
            flags+=[target.get('cflags')]

        flags+=node_get_parent_all(target,'cflags')
        # print('=============>',node_get_parent_all(target,'cflags'))
        # print('defines======================>',target.get('defines') ,target )

        defined=node_get_parent_all(target,'defines')
        if defined:
            flags+=['-D'+item for item in defined]

        return flags

def get_target_ldflags(target):
    flags=[]
    # print('ldflags======>', target.get('ldflags') )
    if target.get('ldflags'):
        flags+=target.get('ldflags')
    if target.get('toolchain'):
        toolchain=nodes_get_type_and_name('toolchain',target.get('toolchain'))
        if toolchain.get('ldflags'):
            flags+= toolchain.get('ldflags')

    flags+=node_get_parent_all(target,'ldflags')

    deps=target.get('deps')
    if deps:
        for d in deps:
            n=nodes_get_type_and_name('target',d)
            n_build_dir=get_build_dir(n,'build-dir')
            n_target=get_build_target(n)
            flags+=['-L'+n_build_dir , '-l'+d]

    flags=list(dict.fromkeys(flags))
    
    return flags

def gcc_build(tool,target,opt={}):
    file_objs=target.get("file-objs")
    if not file_objs:
        log.warn("build target {} not found file {}".
        format(target.get("name"),
        target.get('files')
        ))
    modify_file_objs=[]
    
    log.debug('{} {} build {}'.format(target.get('type'),target.get('name'),file_objs))



    build_dir=get_build_dir(target,'build-dir')
    build_obj_dir=get_build_dir(target,'build-obj-dir')
    
    log.debug('build_dir=>{} build_obj_dir=>{}'.format(build_dir,build_obj_dir))

    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    if not os.path.exists(build_obj_dir):
        os.makedirs(build_obj_dir)


    build_target=get_build_target(target)

    file_obj_dirs=set()
    for file_obj in file_objs:
        obj_name=get_object_name(file_obj)
        build_obj=os.path.join(build_obj_dir,obj_name)

        is_modify=tool.get('is_modify')(file_obj,build_obj)
        if is_modify:
            modify_file_objs.append(file_obj)
            log.debug('file is modify {}'.format(file_obj))
        else:
            log.debug('file is not modify {}'.format(file_obj))
        
        file_obj_dir=os.path.dirname(build_obj)
        file_obj_dirs.add(file_obj_dir)
    
    for file_obj_dir in file_obj_dirs:
        os.makedirs(file_obj_dir,exist_ok=True)

    is_modify_target=False
    if not os.path.exists(build_target):
        is_modify_target=True

    if len(modify_file_objs)<=0 and not is_modify_target:
        return
        
    includedirs=get_include(target)

    cflags=get_target_cflags(target)
    
    total_nodes=len(modify_file_objs)+1
    progress=0
    for obj in modify_file_objs:
        
        obj_name=get_object_name(obj)

        build_obj=os.path.join(build_obj_dir,obj_name)
        log.debug('build_obj=>{} {}'.format(obj,obj_name))

        cmd(tool.get("cc"),[obj]+cflags+includedirs+['-c','-o',build_obj] )

        progress+=1
        print_progress(progress,total_nodes,obj_name, opt)
        
    
    file_objs=[os.path.join(build_obj_dir,get_object_name(item)) for item in file_objs]

    ldflags=get_target_ldflags(target)

    if len(file_objs)==0:
        log.warn('obj file is 0')
        return

    if target.get('kind')=='static':
        cmd(tool.get("ar"),['-r',build_target]+file_objs )
    elif target.get('kind')=='shared':
        flags+=['-shared']
        cmd(tool.get("ld"),file_objs+['-o',build_target]+ ldflags )
    else:
        cmd(tool.get("ld"),file_objs+['-o',build_target]+ ldflags )
    
    progress+=1
    print_progress(progress,total_nodes,build_target,opt)


