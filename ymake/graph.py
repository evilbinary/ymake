# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
import networkx as nx
from node import nodes_get_type_and_name

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
    deps=target.get('deps')
    for d in deps:
        n=nodes_get_type_and_name('target',d)
        graph[d]= n.get('deps')
        build_dep_graph(graph,n,kind)


def find_cycles(graph):
    g = nx.DiGraph(graph)
    try:
        cycles = nx.find_cycle(g, orientation='original')
        return cycles
    except nx.NetworkXNoCycle:
        return []