# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
from automake import init as automake_init
from cmake import init as cmake_init


def toolchains_init():
    automake_init()
    cmake_init()