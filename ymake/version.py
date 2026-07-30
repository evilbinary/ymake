# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
try:
    from importlib.metadata import PackageNotFoundError, version as get_version
except ImportError:
    try:
        from importlib_metadata import PackageNotFoundError, version as get_version
    except ImportError:
        import pkg_resources
        version = pkg_resources.get_distribution('yymake').version

if 'get_version' in globals():
    try:
        version = get_version('yymake')
    except PackageNotFoundError:
        version = 'dev'