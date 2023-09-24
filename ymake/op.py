# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
import re
import os
import subprocess
from .function import *


mod_os = type("os", (), {})
mod_path = type("path", (), {})
mod_string= type("string", (), {})
mod_io= type("io", (), {})

def scriptdir():
    caller_frame = inspect.currentframe().f_back
    caller_file_path = inspect.getframeinfo(caller_frame).filename
    simplified_path = os.path.normpath(caller_file_path)
    dir_name=os.path.dirname(simplified_path)
    return dir_name

def shell(cmd,args=[],env=None):
    cmds = [cmd]+args
    log.debug('shell =>{}'.format(cmds))
    process=None
    if env:
        process = subprocess.Popen(cmds, shell=True, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        process = subprocess.Popen(cmds, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if process.returncode == 0:
        pass
    else:
        log.error(error.decode())
        raise Exception(error.decode())


def cmd(cmd,args=[],env=None):
    cmds = [cmd]+args
    log.debug('cmds =>{}'.format(cmds))

    print(' '.join(cmds))
    process=None
    if env:
        process = subprocess.Popen(cmds, shell=False, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        process = subprocess.Popen(cmds, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)    

    output, error = process.communicate()

    if process.returncode == 0:
        pass
    else:
        log.error(error.decode())
        exit(-1)
        raise Exception(error.decode())

def cmdstr(s):
    cmds=s.split(' ')
    print('cmd str=>{}'.format(s))
    cmd(cmds[0],cmds[1:])

    pass


mod_os.scriptdir=scriptdir
mod_os.execv =cmd
mod_os.exec =cmdstr


def path_join(a,b):
    ret=os.path.join(a,b)

    ret=os.path.normpath(ret)

    return ret



mod_path.join=path_join



def gsub(s,r,replace):
    print('r=',r,'ss=>',s)
    s=s.replace('%','/')
    ret= re.sub(r,replace,s)
    print('ret=>',ret)
    return ret
mod_string.gsub=gsub


mod_io.open=open

