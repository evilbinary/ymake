# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
from .log import log
from .function import *
# from dask.distributed import Client, as_completed
from concurrent.futures import ThreadPoolExecutor
import subprocess


data_list=[]


def get_build_target(target):
    build_dir=node_get_formated(target,'build-dir')
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
    if len(parts)<=1:
        parts = obj_file_name.rsplit('.s', 1)

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
    if target.get('ldflags'):
        flags+=target.get('ldflags')
    toolchain=  target.get('toolchain')
    if not toolchain:
        toolchain_name = node_get_parent(target,'toolchain')
        toolchain=nodes_get_type_and_name('toolchain',toolchain_name)
        
    if toolchain and toolchain.get('ldflags'):
        flags+= toolchain.get('ldflags')

    flags+=node_get_parent_all(target,'ldflags')

    deps=target.get('deps')
    if deps:
        for d in deps:
            n=nodes_get_type_and_name('target',d)
            if n:
                n_build_dir=node_get_formated(n,'build-dir')
                flags+=['-L'+n_build_dir]            
                n_target=get_build_target(n)
                # print('n get kind {} {} target {}'.format(n.get('kind'),n.get('name'),target.get('name') ))

                if n.get('kind')=='static' or n.get('kind')=='shared':
                    flags+=['-l'+d]

    flags=list(dict.fromkeys(flags))
    
    log.debug('ldflags======>{}'.format(flags))
    return flags

def rule_fill(rule,target,key):
    if rule.get(key):
        if target.get('key'):
            target[key].extend(key,rule.get(key))
        else:
            target[key]=[rule.get(key)]

def rule_build(target):
    rules=target.get('rules')
    if not rules:
        return
    for rule_name in rules:
        r=nodes_get_type_and_name('rule',rule_name)
        if not r:
            log.error('not found rule {}'.format(rule_name))
            raise Exception('not found rule '+rule_name)
            return None

        hook=['on_load','after_load','on_config','before_build', 'on_build','after_build']
        for h in hook:
            rule_fill(r,target,h)

def call_hook_event(target,key):
    log.debug('hook run =>{} {}'.format(key,target.get('name') ))
    hook =target.get(key)
    if hook:
        if callable(hook):
            hook(target)
        else:
            for h in hook:
                if h:
                    h(target)

def configfile_build(target):
    configfiles=target.get('configfiles')
    configdir= target.get('configdir')
    configvar = target.get('configvar')
    file_path = target.get('file-path')


    if configfiles and configdir:

        data=get_target_data(target)
        configdir=get_format(configdir,data)

        log.debug('configfiles {}'.format(configfiles))
        for configfile in configfiles:
            f=get_format(configfile,data)

            open_file=os.path.join(file_path,f)
            open_file=os.path.normpath(open_file)

            log.debug('open file {}'.format(open_file))
            file=open(open_file,'r')
            content = file.read()
            if configvar:
                for var in configvar:
                    content=content.replace('${'+var+'}',configvar[var])
            file.close()
            
            out_file=configdir+'/'+f
            log.debug('write file {}'.format(out_file))

            file=open(out_file,'w')
            file.write(content)
            file.close()

def build_prepare(target):
    call_hook_event(target,'on_config')

    files= target.get('files')
    file_objs=target.get('file-objs')
    files=get_list_args(files)
    
    if not file_objs or len(file_objs)< len(files):
        dir_name=target['file-path'] 
        log.debug('prepare files=>'.format(files))
        files=[format_target_var(target,item) for item in files ]
        log.debug('prepare fomrat files=>'.format(files))
        
        match_files=file_match(files,dir_name)
        
        log.debug('{} {} prepare add obj files match {} => {} pwd: {}'.format(target.get('type'),target.get('name') ,files,match_files,os.getcwd() ))
        target['file-objs'].extend(match_files)

    rule_build(target)

def gcc_build(tool,target,opt={}):
    call_hook_event(target,'before_build')

    configfile_build(target)
    file_objs=target.get("file-objs")
    if not file_objs:
        log.warn("build target {} not found file {}".
        format(target.get("name"),
        target.get('files')
        ))
    modify_file_objs=[]
    
    log.debug('{} {} build {}'.format(target.get('type'),target.get('name'),file_objs))

    build_dir=node_get_formated(target,'build-dir')
    build_obj_dir=node_get_formated(target,'build-obj-dir')
    
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
    build_commands=[]

    call_hook_event(target,'on_build')
    for obj in modify_file_objs:
        
        obj_name=get_object_name(obj)

        build_obj=os.path.join(build_obj_dir,obj_name)
        log.debug('build_obj=>{} {}'.format(obj,obj_name))

        build_commands.append([obj_name,tool.get("cc"),[obj]+cflags+includedirs+['-c','-o',build_obj] ])
    
    progress_info={'progress':0,'total_nodes':total_nodes,'opt': opt}
    process_build(build_commands,progress_info)

    file_objs=[os.path.join(build_obj_dir,get_object_name(item)) for item in file_objs]

    ldflags=get_target_ldflags(target)

    if len(file_objs)==0:
        log.warn('obj file is 0')
        return

    build_commands=[]
    if target.get('kind')=='static':
         build_commands.append([build_target,tool.get("ar"),['-r',build_target]+file_objs ])
    elif target.get('kind')=='shared':
        flags+=['-shared']
        build_commands.append([build_target,tool.get("ld"),file_objs+['-o',build_target]+ ldflags ])
    elif target.get('kind')=='binary':
        build_commands.append([build_target,tool.get("ld"),file_objs+['-o',build_target]+ ldflags ])

    process_build(build_commands,progress_info)

    call_hook_event(target,'after_build')

def build_cmd(command,info):
    target=command[0]
    cmd(command[1],command[2])

    log.debug('info=>{}'.format(info))
    
    info['progress']+=1

    print_progress(info['progress'],info['total_nodes'],target, info['opt'])

def process_build(compile_commands,info):

    executor = ThreadPoolExecutor(max_workers=4)
    futures = [executor.submit(build_cmd, command,info ) for command in compile_commands]
    for future in futures:
        log.debug('ret={}'.format(future.result()))
    executor.shutdown()


# def run_job():
    # client = Client()

    # futures = [client.submit(process_data, data) for data in data_list]

    # results = [future.result() for future in as_completed(futures)]

    # for result in results:
    #     print('result==>',result)