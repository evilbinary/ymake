# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
from .function import file_match

def find_library(name,path,**kwargs):
    kind=kwargs.pop('kind','static')
    ext='*.so'
    if kind=='static':
        ext='*.a'

    library={}
    for p in path:
        f=file_match(ext,p)
        print('ff=>',f)
        if len(f)>0:
            setattr(library,'linkdir',f[0])
            return library

    return None