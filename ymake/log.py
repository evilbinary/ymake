# coding:utf-8
# *******************************************************************
# * Copyright 2023-present evilbinary
# * 作者: evilbinary on 01/01/20
# * 邮箱: rootdebug@163.com
# ********************************************************************
import logging
import colorlog
from colorama import Fore, Back, Style, init

# 初始化 colorama
init()

# 配置日志记录
log = logging.getLogger()
log.setLevel(logging.ERROR)


class LowercaseColoredFormatter(colorlog.ColoredFormatter):
    def format(self, record):
        # 调整日志级别为小写形式
        record.levelname = record.levelname.lower()
        return super().format(record)


# 创建彩色日志处理器
handler = colorlog.StreamHandler()
handler.setFormatter(LowercaseColoredFormatter(
    '%(log_color)s%(levelname)s: %(message)s',
    log_colors={
        'debug': 'cyan',
        'info': 'green',
        'warning': 'yellow',
        'error': 'red',
        'critical': 'red,bg_white',
    }
))

# 将处理器添加到日志记录器
log.addHandler(handler)
