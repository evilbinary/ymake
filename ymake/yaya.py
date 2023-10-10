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
import networkx as nx
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

true=True
false=False


def build_graph(project):
    graph={}    
    if project.get('type')=='target':
        target=project
        graph[target.get('name')]= target.get('deps')
    else:
        for target_name in project.get('targets'):
            # print('target_name==>',target_name)

            target_objs=project.get('target-objs')
            if target_objs:
                target=target_objs.get(target_name)
                # print('target_objs=>',target)
                if target:
                    graph[target_name]= target.get('deps')
                else:
                    log.warn('target {} not belong any project'.format(target_name))
    return graph

def find_cycles(graph):
    g = nx.DiGraph(graph)
    try:
        cycles = nx.find_cycle(g, orientation='original')
        return cycles
    except nx.NetworkXNoCycle:
        return []

def compile(project,graph,name):
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
        build_prepare(target)
        toolchain.get('build')(toolchain,target,opt)
        progress = i + 1
        print_progress(progress,total_nodes,node)


    end_time = datetime.datetime.now()
    time_diff=end_time-start_time
    if len(build_target)>0:
        print("{}build success!{} const {}".format(Fore.GREEN,Style.RESET_ALL,time_diff) )
    else:
        print("{}build nothing not target found!{} const {}".format(Fore.GREEN,Style.RESET_ALL,time_diff) )

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

def run(name):
    node_finish()

    target=nodes_get_type_and_name('target',name)
    if target:
        build_prepare(target)
        call_hook_event(target,'before_run')
        call_hook_event(target,'on_run')
    else:
        print('target {}{}{} not found to run, target list: '.format(Fore.MAGENTA,name,Style.RESET_ALL))

        targets=nodes_get_all_type('target')
        for target in targets:
            print('    {}'.format(target.get('name')))

def init():
    global is_init
    root('root')
    add_toolchain_dirs('toolchains')

    # 默认工具
    toolchain('gcc',build=gcc_build)
    if platform.system()=='Darwin':
        add_ldflags('-lSystem')
        add_ldflags('-arch', platform.machine())
    elif platform.system()=='Linux':
        add_ldflags('-lc')
        cur=node_current()
        prefix= cur.get('prefix')
        set_toolset('ld',prefix+'gcc')

    toolchain('arm-none-eabi',prefix='arm-none-eabi-',build=gcc_build)
    toolchain('arm-none-eabi',prefix='arm-none-eabi-',build=gcc_build)
    toolchain('riscv64-unknown-elf',prefix='riscv64-unknown-elf-',build=gcc_build)
    toolchain('i386-elf',prefix='i386-elf-',build=gcc_build)
    toolchain('i686-elf',prefix='i686-elf-',build=gcc_build)

    toolchains_init()
    toolchain_end()


    rule('mode.debug')
    add_ldflags("-g")
    rule_end()

    rule('mode.release')
    rule_end()

    print('welcome to use {}ymake{} {} ,make world happy ^_^!!'.format(Fore.GREEN,Style.RESET_ALL,version))

def process():
    try:
        global mode,jobnum,is_process
        if is_process:
            return

        is_process=True
        # 创建参数解析器
        parser = argparse.ArgumentParser(allow_abbrev=True)

        # 添加参数
        parser.add_argument('-v',nargs='?', default=None, help='verborse info debug error')
        parser.add_argument('-r','-run',nargs='?', default=None, help='run the project target.')
        parser.add_argument('-j',nargs='?', default=1, help='job number')
        parser.add_argument('-m','-mode',nargs='?', default=None, help='build mode debug relase')
        parser.add_argument('-b','-build',nargs='?', default=None, help='build the project target.')

        options=nodes_get_all_type('option')
        for o in options:
            parser.add_argument('--'+o.get('name'),nargs='?', default=o.get('default'), help=o.get('description'))

        # 解析命令行参数
        args = parser.parse_args()

        verborse=args.v

        for o in options:
            n=o.get('name').replace('-','_')
            v=getattr(args, n)
            o['value']=v

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
        if args.b:
            build(args.b)
        else:
            build(args.b)
        if args.r:
            run(args.r)
    except (KeyboardInterrupt):
        pass

if __name__ == 'yaya':
    init()
    ya=os.path.join(os.getcwd(),"./ya.py")
    ya=os.path.normpath(ya)
    add_subs(ya)
    process()

else:
    pass
