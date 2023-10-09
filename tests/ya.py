# coding:utf-8
# *******************************************************************
# * Copyright 2021-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
import sys
sys.path.append('..')
sys.path.append('.')
sys.path.append('../..')

# from ymake.yaya import *

project("yiyiya",
    version='12.0',
    desc='yiyiya is an os',
    targets=[
        'a',
        'b'
    ]
)

add_subs('./**/*.py')
