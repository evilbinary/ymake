# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
from log import log
from function import *
# from dask.distributed import Client, as_completed
from concurrent.futures import ThreadPoolExecutor
import subprocess
from collections import OrderedDict
from graph import build_graph,find_cycles,build_dep_graph,get_dep_order

data_list=[]


def get_build_target(target,path='',name=''):
    build_dir=node_get_formated(target,'build-dir')
    ext=''
    prefix=''
    if target.get('kind')=='static':
        ext='.a'
        prefix='lib'
    elif target.get('kind')=='shared':
        ext='.so'
        prefix='lib'
    if not name:
        name=target.get("name")
    if target.get('filename'):
        name= target.get('filename')
    
    build_tool=target.get('build-tool')
    if build_tool:
        d=build_tool.get('build-dir')
        if d:
            build_dir=d
            name=build_tool.get('name')
            if build_tool.get('filename'):
                name= build_tool.get('filename')

    out_name=os.path.join(build_dir+path,prefix+name+ext)
    # print('build target name ',out_name,build_dir,target.get("name"))
    return out_name

def get_object_name(obj,full=False):
    obj_file_name=obj
    if full:
        obj_file_name=obj
    parts=[]
    if obj_file_name.endswith('.cpp'):
        parts = obj_file_name.rsplit('.cpp', 1)
    else:
        parts = obj_file_name.rsplit('.c', 1)
        if len(parts)<=1:
            parts = obj_file_name.rsplit('.s', 1)

    new_obj_name = '.o'.join(parts)
    return new_obj_name


def get_target_include(target):
    includes=[]
    includes+=get_include(target)

    deps=target.get('deps')
    if deps:
        for d in deps:
            n=nodes_get_type_and_name('target',d)
            if n:
                include=get_includedirs(n)

                n_build_dir=node_get_formated(n,'build-dir')
                n_build_lib_dir =node_get_formated(n,'build-lib-dir')
                if not n_build_lib_dir:
                    tool=node_get_parent(n,'toolchain')
                    build_prepare(tool,n)
                    n_build_lib_dir =node_get_formated(n,'build-lib-dir')

                if n_build_lib_dir:
                    include=['-I' + os.path.relpath(os.path.join(n_build_lib_dir,item)) for item in include]
                    include=include + get_include(n)
                    includes+=include
                else:
                    include=['-I' + os.path.relpath(os.path.join(n_build_dir,item)) for item in include]
                    include=include + get_include(n)
                    includes+=include
                includes+=get_target_include(n)

    includes=list(set(includes))
    return includes

def get_target_cxxflags(target):
        flags=[]
        if target.get('cxxflags'):
            flags+=target.get('cxxflags')

        flags+=node_get_parent_all(target,'cxxflags')
        # print('=============>',node_get_parent_all(target,'cflags'))
        # print('defines======================>',target.get('defines') ,target )

        defined=node_get_parent_all(target,'defines')
        if defined:
            flags+=['-D'+item for item in defined]

        return flags

def get_target_cflags(target):
        flags=[]

        flags+=node_get_parent_all(target,'cflags')
        # print('=============>',node_get_parent_all(target,'cflags'))

        defined=node_get_parent_all(target,'defines')
        if defined:
            flags+=['-D'+item for item in defined]

        return flags

def get_lib_name(path_name):
    lib=''.join(path_name.rsplit('/')[-1:])
    lib=lib.replace('.a','')
    lib=lib.replace('.so','')
    if lib.startswith('lib'):
        lib=lib[3:]
    return lib

def get_target_ldflags(target):
    flags=[]
    if target.get('ldflags'):
        flags+=target.get('ldflags')
    toolchain= target.get('toolchain')
    if not toolchain:
        toolchain_name = node_get_parent(target,'toolchain')
        toolchain=nodes_get_type_and_name('toolchain',toolchain_name)
        
    if toolchain and toolchain.get('ldflags'):
        flags+= toolchain.get('ldflags')

    flags+=node_get_parent_all(target,'ldflags')

    deps=target.get('deps')
    if deps:
        topological_order= get_dep_order(target,['static','shared','lib'])
        log.debug('dep orders {}'.format(topological_order))
        for d in topological_order:
            n=nodes_get_type_and_name('target',d)
            if not n:
                continue            
            if not n.get('kind') in ['static','shared','lib']:
                continue
            
            if n.get('ldflags'):
                flags+=n.get('ldflags')
            
            n_build_dir=node_get_formated(n,'build-dir')
            if n.get('build-tool'):
                ext='.a'
                if n.get('kind')=='shared':
                    ext='.so'
                lib_files=file_match(n_build_dir+'/*'+ext)
                log.debug('====>lib_file {}'.format(lib_files))
                flags+=['-L'+n_build_dir]
                for lib in lib_files:
                    flags+=['-l'+get_lib_name(lib)]
            else:
                lib_file=get_build_target(n)
                if os.path.exists(lib_file):
                    flags+=['-L'+n_build_dir]
                    flags+=['-l'+d]




    log.debug('ldflags no uniq======>{} {}'.format(len(flags),target.get('name')))

    flags=list(OrderedDict.fromkeys(flags))
    lib_path_flags = []
    lib_name_flags = []
    flags_rest =[]
    for f in flags:
        if f.startswith('-L'):
            lib_path_flags.append(f)
        elif f.startswith('-l'):
            lib_name_flags.append(f)
        else:
            flags_rest.append(f)

    flags=lib_path_flags+flags_rest+lib_name_flags
    log.debug('ldflags======>{} len: {}'.format(flags,len(flags)))
    return flags

def rule_fill(rule,target,key):
    val=rule.get(key)
    if not val:
        return
    
    log.debug('apply rule {} key={} target name ={} target key {} rule key=>{}'.format(rule.get('name'),key,target.get('name'),target.get(key),val ))

    if not isinstance(val,list):
        val=[val]

    node_op_extend(target,key,val,True,True)


def rule_build(target):
    rules=target.get('rules')
    if not rules:
        rules=[]
    r=node_get_parent_all(target,'rules')
    if r:
        rules+=r
    if not rules:
        return
    rules=list(set(rules))
    for rule_name in rules:
        r=nodes_get_type_and_name('rule',rule_name)
        if not r:
            log.error('not found rule {}'.format(rule_name))
            raise Exception('not found rule '+rule_name)
            return None

        hook=['on_load','after_load','on_config','before_build', 'on_build','after_link','after_build','cflags','ldflags']
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

def tool_build(target):
    tool=target.get('build-tool')
    if tool:
        toolchain_name=tool.get('toolchain')
        toolchain=nodes_get_type_and_name('toolchain',toolchain_name)
        if toolchain:
            toolchain.get('build')(toolchain,target)

def build_prepare(tool,target,opt={}):
    rule_build(target)

    call_hook_event(target,'on_load')

    call_hook_event(target,'on_config')

    files= target.get('files')
    file_objs=target.get('file-objs')
    files=get_list_args(files)
    
    build_tool=target.get('build-tool')
    if build_tool:
        build_tool.toolchain()['build_prepare'](tool,target)

    if not file_objs or len(file_objs)< len(files):
        dir_name=target['file-path'] 
        log.debug('prepare files=>{}'.format(files))
        files=[format_target_var(target,item) for item in files ]
        log.debug('prepare format files=>{}'.format(files))
        
        build_obj_dir=node_get_formated(target,'build-obj-dir')

        match_files=file_match(files,dir_name)
        obj_files=[]
        
        kind=None
        normal_kind=['c','cc','cxx','cpp','s','h','hpp']
        for f in match_files:
            ext=get_ext(f)
            obj_name=get_object_name(f)
            build_obj=os.path.join(build_obj_dir,obj_name)
            obj_files.append({
                'obj': build_obj,
                'src': f
                })
            if ext not in normal_kind:
                kind='rule'

        if len(match_files)<=0:
            match_files=file_match(files)            
            for f in match_files:
                obj_name=get_object_name(f)
                obj_files.append({
                    'obj': f,
                    'src': f
                    })
                ext=get_ext(f)
                if ext not in normal_kind:
                    kind='rule'
        if kind:
            target.set('kind',kind)
        
        log.debug('{} {} prepare add obj files match {} => {} pwd: {}'.format(target.get('type'),target.get('name') ,files,match_files,os.getcwd() ))
        target['file-objs'].extend(obj_files)


def get_ext(name):
    if not name:
        return ''
    l=name.rsplit('.')
    if len(l)<=1:
        return ''
    else:
        return l[len(l)-1]

def gcc_clean(tool,target,opt={}):
    build_dir=node_get_formated(target,'build-dir')
    build_obj_dir=node_get_formated(target,'build-obj-dir')
    build_target=get_build_target(target)
    file_objs=target.get("file-objs")

    for obj in file_objs:
        if os.path.exists(obj['obj']):
            os.remove(obj['obj'])

    if os.path.exists(build_target):
        os.remove(build_target)

def gcc_build(tool,target,opt={}):
    call_hook_event(target,'before_build')

    tool_build(target)
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

    jobnum= node_get_parent(target,'jobnum')

    log.debug('build_dir=>{} build_obj_dir=>{}'.format(build_dir,build_obj_dir))

    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    if not os.path.exists(build_obj_dir):
        os.makedirs(build_obj_dir)


    build_target=get_build_target(target)

    is_modify_obj=False
    file_obj_dirs=set()
    for file in file_objs:
        file_src=file.get('src')
        file_obj=file.get('obj')

        is_modify=tool.get('is_modify')(file_src,file_obj)
        if is_modify:
            modify_file_objs.append(file)
            log.debug('file is modify {}'.format(file_obj))
            is_modify_obj=True
        else:
            log.debug('file is not modify {}'.format(file_obj))
        
        file_obj_dir=os.path.dirname(file_obj)
        file_obj_dirs.add(file_obj_dir)
    
    for file_obj_dir in file_obj_dirs:
        if file_obj_dir:
            os.makedirs(file_obj_dir,exist_ok=True)

    is_modify_target=False
    if not os.path.exists(build_target):
        is_modify_target=True
    
    # deps change
    deps=target.get('deps')
    for d in deps:
        n=nodes_get_type_and_name('target',d)
        t=get_build_target(n)
        is_modify=tool.get('is_modify')(t,t)
        if is_modify:
            is_modify_target=True


    if len(modify_file_objs)<=0 and not is_modify_target:
        call_hook_event(target,'after_link')
        call_hook_event(target,'after_build')
        return
        
    includedirs=get_target_include(target)
    log.debug("includedirs {}".format(includedirs))

    cflags=get_target_cflags(target)
    log.debug('{} cflags {}'.format(target.get("name"),cflags))
    
    cxxflags=get_target_cxxflags(target)
    log.debug('{} cxxflags {}'.format(target.get("name"),cxxflags))

    total_nodes=len(modify_file_objs)+1
    build_commands=[]

    extend=target.get('extensions')
    file_rules=target.get('file-rules')
    
    if is_modify_target or is_modify_obj:
        call_hook_event(target,'on_build')

    for f in modify_file_objs:
        src=f.get('src')
        obj=f.get('obj')
        
        obj_name=get_object_name(obj)

        log.debug('build_obj=>{} {}'.format(obj,obj_name))

        ext=get_ext(obj)

        if src[-2:] in [".c",".s"]:
            build_commands.append([obj_name,tool.get("cc"),[src]+cflags+includedirs+['-c','-o',obj] ])
        elif src.endswith(".cpp") or obj_name.endswith(".cc"):
            build_commands.append([obj_name,tool.get("cxx"),[src]+cxxflags+includedirs+['-c','-o',obj] ])
        elif src.endswith(".o"):
            pass
        elif ext=='' or ext=='bin':
            pass
        elif file_rules and ext ==file_rules:
            pass
        elif extend and ext in extend:
            pass
        else:
            raise Exception(target.get('name')+' not support build '+obj_name+' '+obj)
    

    progress_info={'progress':0,'total_nodes':total_nodes,'opt': opt}
    process_build(build_commands,progress_info,jobnum)

    file_objs=[item.get('obj') for item in file_objs]

    ldflags=get_target_ldflags(target)
    log.debug('ldflags {}'.format(ldflags))

    if len(file_objs)==0:
        log.warn('obj file is 0')
        return

    build_target_commands=[]
    if target.get('kind')=='static':
         build_target_commands.append([build_target,tool.get("ar"),['-r',build_target]+file_objs ])
         process_build(build_target_commands,progress_info,jobnum)
    elif target.get('kind')=='shared':
        flags+=['-shared']
        build_target_commands.append([build_target,tool.get("ld"),file_objs+['-o',build_target]+ ldflags ])
        process_build(build_target_commands,progress_info,jobnum)
    elif target.get('kind')=='binary':
        build_target_commands.append([build_target,tool.get("ld"),file_objs+['-o',build_target]+ ldflags ])
        process_build(build_target_commands,progress_info,jobnum)
    else:

        pass
    

    call_hook_event(target,'after_link')
    call_hook_event(target,'after_build')

    # is_modify=tool.get('is_modify')(build_target,build_target)

def build_cmd(command,info):
    target=command[0]
    cmd(command[1],command[2])

    log.debug('info=>{}'.format(info))
    
    info['progress']+=1

    print_progress('compile',info['progress'],info['total_nodes'],target, info['opt'])

def process_build(compile_commands,info,jobnum):
    executor = ThreadPoolExecutor(max_workers=jobnum)
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