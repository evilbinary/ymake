# coding:utf-8
# *******************************************************************
# * Copyright 2021-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
target('c',
    kind='binary',
    deps=['b'],
    files=[
        './*.c',
    ]
)

