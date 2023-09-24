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
import shutil
import glob
import math

mod_os = type("os", (), {})
mod_path = type("path", (), {})
mod_string= type("string", (), {})
mod_io= type("io", (), {})

mod_math= type("math", (), {})

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
    s=s.replace('  ',' ')
    s=s.replace('  ',' ')
    cmds=s.split(' ')
    cmds=[s for s in cmds if s != '']
    
    print('cmdstr cmds=>{}'.format(cmds))
    cmd(cmds[0],cmds[1:])

    pass

def cp(src,dest):
    # cmdstr('cp -r '+src+' '+dest)

    file_list = glob.glob(src)
    print('file-list',file_list)
    # 逐个复制文件
    for file_path in file_list:
        if os.path.isdir(file_path):
            shutil.copytree(file_path, dest, dirs_exist_ok=True)
        else:
            shutil.copy(file_path,dest)

mod_os.scriptdir=scriptdir
mod_os.execv =cmd
mod_os.exec =cmdstr
mod_os.cp = cp
mod_os.filesize=os.path.getsize

def path_join(a,b):
    ret=os.path.join(a,b)

    ret=os.path.normpath(ret)

    return ret

def find(str1,str2):
    if not str1:
        return False

    return str1.find(str2)>0


mod_path.join=path_join
mod_path.directory=os.path.dirname


def gsub(s,r,replace):
    print('r=',r,'ss=>',s)
    s=s.replace('%','/')
    ret= re.sub(r,replace,s)
    print('ret=>',ret)
    return ret
mod_string.gsub=gsub
mod_string.find=find

mod_io.open=open

mod_math.ceil=math.ceil

