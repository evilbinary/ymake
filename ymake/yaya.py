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
from .log import log
from .function import *
from .builder import *

version='0.1.6'

verborse=''


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

def compile(project,graph):
    G = nx.DiGraph(graph)
    # 执行拓扑排序
    topological_order = list(nx.topological_sort(G))
    total_nodes = len(topological_order)
    toolchain_name=project.get('toolchain')

    # 根据拓扑排序的顺序反向遍历节点，并编译代码
    compiled_code = []
    start_time = datetime.datetime.now()
    for i,node in enumerate(reversed(topological_order)):
        # 编译节点对应的代码
        # print('node===>',node,project.get('target-objs'))

        target=project.get('target-objs').get(node)
        if not target:
            log.error('not found target {}'.format(node))
            return
        if target.get('toolchain'):
            toolchain_name=target.get('toolchain')

        toolchain=nodes_get_type_and_name('toolchain',toolchain_name)
        if not toolchain:
            log.error('not found toolchain {}'.format(toolchain_name))
            break

        opt={
            'progress':i,
            'total_nodes':total_nodes
        }
        toolchain.get('build')(toolchain,target,opt)
        progress = i + 1
        print_progress(progress,total_nodes,node)


    end_time = datetime.datetime.now()
    time_diff=end_time-start_time
    print("{}build success!{} const {}".format(Fore.GREEN,Style.RESET_ALL,time_diff) )
    

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

def build():
    nodes.extend(node_stack)
    node_stack.clear()

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
            compile(p,graph)



# 默认工具
toolchain('gcc',build=gcc_build)
if platform.system()=='Darwin':
    add_ldflags('-lSystem')
    add_ldflags('-arch', platform.machine())
elif platform.system()=='Linux':
    add_ldflags('-lc')

toolchain('arm-none-eabi',prefix='arm-none-eabi-',build=gcc_build)
toolchain('arm-none-eabi',prefix='arm-none-eabi-',build=gcc_build)
toolchain('riscv64-unknown-elf',prefix='riscv64-unknown-elf-',build=gcc_build)
toolchain('i386-elf',prefix='i386-elf-',build=gcc_build)
toolchain('i686-elf',prefix='i686-elf-',build=gcc_build)
toolchain_end()

root('root')

print('welcome to use {}ymake{} {} ,make world happy ^_^!!'.format(Fore.GREEN,Style.RESET_ALL,version))


# 创建参数解析器
parser = argparse.ArgumentParser(description='help')

# 添加参数
parser.add_argument('target',nargs='?', default=None, help='build target')
parser.add_argument('--option',nargs='?', default=None, help='option')
parser.add_argument('-v',nargs='?', default=None, help='verborse debug')

# 解析命令行参数
args = parser.parse_args()

verborse=args.v
if args.v=='D':
    log.setLevel(logging.DEBUG)
    
