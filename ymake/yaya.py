# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
import os
import math
import platform 
import sys

module_path=['..',
    '.',
    '../../',
    '../../..',
    'xenv']
sys.path.extend(module_path)

import json
from colorama import Fore, Back, Style, init
import fnmatch
import types
import argparse
import inspect
import hashlib
import datetime
import logging
from log import log
from function import *
from builder import *
from toolchain import toolchains_init
from version import version
from globa import verborse,jobnum,mode,is_init,is_process
from graph import build_graph,find_cycles

true=True
false=False
args=None
parser=None


def compile(project,graph,name):
    G = nx.DiGraph(graph)
    # 执行拓扑排序
    topological_order = [] 

    toolchain_name=project.get('toolchain')

    if name:
        t=project.get('target-objs').get(name)
        if not t:
            log.error('not found target {}'.format(name))
            return
        topological_order=get_dep_order(t)
        topological_order.reverse()
        topological_order.append(name)
    else:
        topological_order=(list(nx.topological_sort(G)))
        topological_order.reverse()
   
    total_nodes=len(topological_order)

    # 根据拓扑排序的顺序反向遍历节点，并编译代码
    compiled_code = []
    start_time = datetime.datetime.now()
    build_target=[]
    for i,node in enumerate(topological_order):
        # 编译节点对应的代码
        # print('node===>',node,project.get('target-objs'))

        target=project.get('target-objs').get(node)

        if not target:
            log.error('not found target {}'.format(node))
            return
        if target.get('toolchain'):
            toolchain_name=target.get('toolchain')
        build_target.append(target)

        toolchain=nodes_get_type_and_name('toolchain',toolchain_name)
        if not toolchain:
            log.error('not found toolchain {}'.format(toolchain_name))
            break

        opt={
            'progress':i,
            'total_nodes':total_nodes
        }
        bp=toolchain.get('build_prepare')
        if bp:
            bp(toolchain,target,opt)
        toolchain.get('build')(toolchain,target,opt)
        progress = i + 1
        print_progress('compile',progress,total_nodes,node)


    end_time = datetime.datetime.now()
    time_diff=end_time-start_time
    if len(build_target)>0:
        print("{}build success!{} cost {}".format(Fore.GREEN,Style.RESET_ALL,time_diff) )
    else:
        print("{}build nothing not target found!{} cost {}".format(Fore.GREEN,Style.RESET_ALL,time_diff) )

class CustomEncoder(json.JSONEncoder):
    cache={}
    def default(self, obj):
        try:        
            if callable(obj) or isinstance(obj, type):
                return str(obj)
            if not cache.get(obj):
                return super().default(obj)
                cache[obj]=True
        except TypeError:
            pass

def node_dump(node):
    if not node:
        return
    d=json.dumps(node,cls=CustomEncoder,indent=4)
    print(node.get('type'),d )
    pass


def build(name=None):
    node_finish()
    for p in nodes:
        if not p.get('type') in ['project']:
            continue
        # print('project=>',p)
        graph=build_graph(p)
        # print('graph=>',graph)

        if len(graph)<=0:
            print('{}build nothing finish.{}'.format(Fore.GREEN,Style.RESET_ALL))
            continue
        cycles=find_cycles(graph)
        
        if len(cycles)>0:
            print("cycle depency:")
            for cycle in cycles:
                print(' -> '.join(cycle))
            print('build failed')
        else:
            compile(p,graph,name)



def clean_target(project,graph,name):
    G = nx.DiGraph(graph)
    # 执行拓扑排序
    topological_order = list(nx.topological_sort(G))
    total_nodes = len(topological_order)
    toolchain_name=project.get('toolchain')

    # 根据拓扑排序的顺序反向遍历节点，并编译代码
    compiled_code = []
    start_time = datetime.datetime.now()
    build_target=[]
    for i,node in enumerate(reversed(topological_order)):
        # 编译节点对应的代码
        # print('node===>',node,project.get('target-objs'))

        target=project.get('target-objs').get(node)
        if name and target:
            if not (target.get('name')==name ):
                continue
        if not target:
            log.error('not found target {}'.format(node))
            return
        if target.get('toolchain'):
            toolchain_name=target.get('toolchain')
        build_target.append(target)

        toolchain=nodes_get_type_and_name('toolchain',toolchain_name)
        if not toolchain:
            log.error('not found toolchain {}'.format(toolchain_name))
            break

        opt={
            'progress':i,
            'total_nodes':total_nodes
        }
        toolchain.get('build_prepare')(toolchain,target,opt)
        toolchain.get('clean')(toolchain,target,opt)
        progress = i + 1
        print_progress('clean',progress,total_nodes,node)


    end_time = datetime.datetime.now()
    time_diff=end_time-start_time
    if len(build_target)>0:
        print("{}clean success!{} cost {}".format(Fore.GREEN,Style.RESET_ALL,time_diff) )
    else:
        print("{}clean nothing not target found!{} cost {}".format(Fore.GREEN,Style.RESET_ALL,time_diff) )

def clean(name=None):
    node_finish()
    for p in nodes:
        if not p.get('type') in ['project']:
            continue
        # print('project=>',p)
        graph=build_graph(p)
        # print('graph=>',graph)

        if len(graph)<=0:
            print('{}clean nothing finish.{}'.format(Fore.GREEN,Style.RESET_ALL))
            continue
        cycles=find_cycles(graph)
        
        if len(cycles)>0:
            print("cycle depency:")
            for cycle in cycles:
                print(' -> '.join(cycle))
            print('clean failed')
        else:
            clean_target(p,graph,name)


def run(name):
    node_finish()

    target=nodes_get_type_and_name('target',name)
    if target:
        call_hook_event(target,'before_run')
        call_hook_event(target,'on_run')
    else:
        print('target {}{}{} not found to run, target list: '.format(Fore.MAGENTA,name,Style.RESET_ALL))

        targets=nodes_get_all_type('target')
        for target in targets:
            print('    {}'.format(target.get('name')))
    
def load():
    ya=os.path.join(os.getcwd(),"./ya.py")
    ya=os.path.normpath(ya)
    add_subs(ya)

def process_option(parser):
    options=nodes_get_all_type('option')
    for o in options:
        if o.get('args'):
            parser.add_argument('--'+o.get('name'),nargs=o.get('args'), default=o.get('default'), help=o.get('description'))
        else:
            parser.add_argument('--'+o.get('name'),action='store_true', default=o.get('default'), help=o.get('description'))
    return options

def init():
    global is_init,parser,args,verborse
    root('root')
    add_toolchain_dirs('toolchains')
    
    # 默认工具
    toolchain('gcc',build=gcc_build,build_prepare=build_prepare)
    if platform.system()=='Darwin':
        add_ldflags('-lSystem')
        add_ldflags('-arch', platform.machine())
    elif platform.system()=='Linux':
        add_ldflags('-lc')
        cur=node_current()
        prefix= cur.get('prefix')
        set_toolset('ld',prefix+'gcc')

    toolchain('arm-none-eabi',
        prefix='arm-none-eabi-',
        build=gcc_build,
        build_prepare=build_prepare,
        clean=gcc_clean)
    toolchain('riscv64-unknown-elf',
        prefix='riscv64-unknown-elf-',
        build=gcc_build,
        build_prepare=build_prepare,
        clean=gcc_clean)
    toolchain('i386-elf',
        prefix='i386-elf-',
        build=gcc_build,
        build_prepare=build_prepare,
        clean=gcc_clean)
    toolchain('i686-elf',
        prefix='i686-elf-',
        build=gcc_build,
        build_prepare=build_prepare,
        clean=gcc_clean)

    toolchains_init()
    toolchain_end()


    rule('mode.debug')
    def build_config(target):
        if is_mode("debug"):
            target.add('cflags',"-g")
        pass
    on_config(build_config)
    rule_end()

    rule('mode.release')
    def build_config(target):
        if is_mode("release"):
            target.add('cflags',"-O2")
        pass
    on_config(build_config)
    rule_end()

    print('welcome to use {}ymake{} {} ,make world happy ^_^!!'.format(Fore.GREEN,Style.RESET_ALL,version))

    # 创建参数解析器
    parser = argparse.ArgumentParser(allow_abbrev=True,add_help=False)

    parser.add_argument('-v',nargs='?', default=None, help='verborse info debug error')
    parser.add_argument('-r','-run',nargs='?', default=None, help='run the project target.')
    parser.add_argument('-j',nargs='?', default=1, help='job number')
    parser.add_argument('-m','-mode',nargs='?', default=None, help='build mode debug release')
    parser.add_argument('-b','-build',nargs='?', default=None, help='build the project target.')
    parser.add_argument('-c','-clean',nargs='?', default=None, help='clean the project target.')
    parser.add_argument('-p','-plat',nargs='?', default=None, help='select the project platform.')

    parser.add_argument('-h','--help',action='store_true', default=None, help='help')

    args,unknown = parser.parse_known_args()

    verborse=args.v
    if args.help :
        load()
        process_option(parser)
        # 解析命令行参数
        args = parser.parse_args()
        parser.print_help()

        exit(0)
   
    log.debug('args=>',unknown)
    # 添加参数
    for name in unknown:
        n=name.replace('--','')
        option(n,value=True)        

    if args.v=='D':
        log.setLevel(logging.DEBUG)
    elif args.v=='I':
        log.setLevel(logging.INFO)
    elif args.v=='W':
        log.setLevel(logging.WARN)
    if args.j:
        jobnum=args.j
        set_config('jobnum',int(jobnum))
    if args.m:
        mode=args.m
        set_config('mode',mode)
    if args.p:
        set_defaultplat(args.p)

def process():
    try:
        global mode,jobnum,is_process
        if is_process:
            return

        is_process=True
       
        if args.c:
            clean(args.c)
        elif args.b:
            build(args.b)
        else:
            build(args.b)
        if args.r:
            run(args.r)
    except (KeyboardInterrupt):
        pass
    except Exception as e:
        if verborse=='D':
            raise e
        pass

if __name__ == 'yaya':
    init()
    load()
    process()

else:
    pass
