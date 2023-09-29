# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
from .function import file_match
import os
from .builder import get_lib_name

class DotDict(dict):
    def __getattr__(self, attr):
        return self.get(attr)

def find_library(name,path,**kwargs):
    kind=kwargs.pop('kind','static')
    ext='*.so'
    if kind=='static':
        ext='*.a'
    name='lib'+name

    library=DotDict()
    for p in path:
        f=file_match(p+name+ext)
        print('ff=>',f)
        if len(f)>0:
            lib=f[0]
            library['filename']=os.path.basename(lib)
            library['linkdir']=os.path.dirname(lib)
            library['link']=get_lib_name(lib)
            library['kind']=kind
            return library

    return None