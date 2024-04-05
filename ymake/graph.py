# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
import networkx as nx
from node import nodes_get_type_and_name,nodes_get_all_type
from log import log

def build_graph(project,kind=None):
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
                if kind :
                    if target and target.get('kind') in kind:
                        graph[target_name]= target.get('deps')
                # print('target_objs=>',target)
                else:
                    if target:
                        graph[target_name]= target.get('deps')
                    else:
                        log.warn('target {} not belong any project'.format(target_name))
    return graph

def build_dep_graph(graph,target,kind=None):
    try:
        deps=target.get('deps')
        for d in deps:
            n=nodes_get_type_and_name('target',d)
            if not n:
                log.warn('target %s get deps %s not found',target.get('name'),d)
                log.warn('target info is %s',target)
                continue
            build_dep_graph(graph,n,kind)
            if n:
                graph[d]= n.get('deps')
    except Exception as ex:
        if target and target.get('name'):
            log.error('target %s get deps erro ',target.get('name'),ex)
        else:
            log.error('target is null get deps erro',ex)

def get_dep_order(target,kind=None,reverse=False):
    project=nodes_get_all_type('project')
    graph={}
    if len(project)>0:
        build_dep_graph(graph,target,kind)
    if graph.get(target.get('name')):
        del graph[target.get('name')]
    G = nx.DiGraph(graph)
    # 执行拓扑排序
    topological_order = list(nx.topological_sort(G))
    single=list(nx.isolates(G))
    for i in single:
        topological_order.remove(i)
    topological_order+=single
    if reverse:
        topological_order.reverse()
    return topological_order

def find_cycles(graph):
    g = nx.DiGraph(graph)
    try:
        cycles = nx.find_cycle(g, orientation='original')
        return cycles
    except nx.NetworkXNoCycle:
        return []