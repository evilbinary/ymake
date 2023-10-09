# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
import sys
sys.path.append('..')
sys.path.append('.')
sys.path.append('../..')

from ymake.yaya import *
from ymake.cmake import cmake,cmake_end
from ymake.automake import automake,automake_end

import pytest


def test_file_match():
    result =file_match('tests/**/*.c')
    print('files=>',result)
    assert result == ['tests/a/a.c', 'tests/c/c.c', 'tests/b/b2.c', 'tests/b/b1.c', 'tests/b/b4.c', 'tests/b/b.c', 'tests/b/b3.c']

def test_grph_cycle():
    graph = {
        'A': ['B', 'C'],
        'B': ['C'],
        'C': ['A'],
        'D': ['E'],
        'E': ['D']
    }
    result=find_cycles(graph)
    print('result=>',result)


def test_project():
    cur=node_current()
    node_dump(cur)

def test_normal_project():
    project("yiyiya",
        version='12.0',
        desc='yiyiya is an os',
        targets=[
            'aaa',
            'bbb'
        ]
    )


    target('aaa',
        kind='bin',
        deps=['bbb','cccc'],
        files=[
            'aa/*.c',
            'abc/*.b'
        ]
    )

    target('bbb')
    add_kind("static")
    add_files("bb.c")
    add_deps("a","f")


    target('cccc')
    add_kind("static")
    add_files("ccc1.c")
    add_deps("b","c")


    target('c')
    add_kind("static")
    add_files("c1.c")


    target('a')
    add_kind("static")
    add_files("a1.c")

    target('b')
    add_kind("static")
    add_files("b1.c","b2.c","b3.c")

    target('f')
    add_kind("static")
    add_files("f1.c")

    build()


def test_set_arch():
    project('aaa')
    set_arch('aaa')
    assert 'aaa'==get_arch()

    target('a')
    assert 'aaa'==get_arch()

    target('b')
    assert 'aaa'==get_arch()

    target('c')
    assert 'aaa'==get_arch()
    set_arch('cccc')
    assert 'cccc'==get_arch()

    target('d')
    assert 'aaa'==get_arch()

def test_add_cflags():

    root('root')

    add_cflags('-lroot')
    cur=node_current()
    assert 'root'==cur.get('name')

    project('aaa')

    add_cflags('-la')
    assert ['-la']==get_cflags()

    add_cflags('-lb')
    assert ['-la','-lb']==get_cflags()

    project_end()

    assert ['-lroot']==get_cflags()
    
    cur=node_current()
    assert 'root'==cur.get('name')

def test_add_cflags_array():
    arch_cflags=['-mcpu=cortex-a7', '-mtune=cortex-a7', '-mfpu=vfpv4', '-mfloat-abi=softfp']
    plat_cflags= ['-nostdlib', '-nostdinc']

    cflags_before=get_cflags()+arch_cflags+plat_cflags

    add_cflags(arch_cflags)
    add_cflags(plat_cflags)

    
    cflags_after=get_cflags()

    assert cflags_before ==cflags_after

def test_target_scope():

    add_cflags('-lroot')

    target('a')
    add_cflags('-la')
    assert ['-la']==get_cflags()
    target('b')

    add_cflags('-lb')
    assert ['-lb']==get_cflags()
    target_end()

    assert None==get_cflags()
    

def test_set_kind():
    project('project-kind')
    set_kind('static')

    assert 'static'==node_get('kind')

    p=nodes_get_type_and_name('project','project-kind')

    assert p.get('name')=='project-kind'

    target('a')
    set_kind('binary')
    assert 'binary'==node_get('kind')


def test_add_defines():
    target('a')
    add_defines('A')

    cur=node_current()
    assert ['A']==cur.get('defines')

    add_defines('A','B','C')

    assert ['A','A','B','C']==cur.get('defines')


def test_cflags():

    project('project-cflags')

    add_cflags('-la','-lb')

    target('ccc')

    add_cflags('-lc')

    cflags=get_cflags()
    assert ['-lc']==cflags

    cur=node_current()

    print('--->',cur.get('parent').get('name') )
    print('--->',cur.get('parent').get('cflags') )


    assert ['-lc', '-la', '-lb']==node_get_parent_all(cur,'cflags')
    

def test_exend():
    f=['-mcpu=cortex-a7', '-mtune=cortex-a7', '-mfpu=vfpv4', '-mfloat-abi=softfp']
    add_cflags(f)

    cflags=get_cflags()
    print('cflags->',cflags)

    add_cflags(f)

    # assert ['-lc', '-la', '-lb']==cflags


def test_rule():
    
    project('test_rule')

    rule("markdown")
    set_extensions(".md", ".markdown")
    on_build_file(lambda target, sourcefile, opt:
        os.cp(sourcefile, path.join(target.targetdir(), path.basename(sourcefile) + ".html"))
        )
    

    target("test")

    set_kind("binary")

    # Make the test target support the construction rules of the markdown file
    add_rules("markdown")

    # Adding a markdown file to build
    add_files("src/*.md")
    add_files("src/*.markdown")

    target_end()

    n=node_current()
    print('n====>',n)

    build()

def test_automake():

    automake('test')


def test_option():
    option('abc')

    a=has_config('abc')
    assert a==True

    a=has_config('abc1')
    assert a==False

def test_set_config():

    set_config('abc','111')

    abc=get_config('abc')

    assert abc=='111'

    set_config('a','1','2')
    a=get_config('a')
    assert a==['1','2']


    
def test_set_config_array():


    arch_cflags=['-mcpu=cortex-a7', '-mtune=cortex-a7', '-mfpu=vfpv4', '-mfloat-abi=softfp']
    plat_cflags= ['-nostdlib', '-nostdinc']

    set_config('cflags',arch_cflags,plat_cflags)

    assert get_config('cflags')==arch_cflags+plat_cflags
