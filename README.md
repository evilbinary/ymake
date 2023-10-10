# ymake
ymake is a make dsl build tools


## 安装

```bash
pip install yymake
```

## 使用

新建ya.py

```python
project("yiyiya",
    version='12.0',
    desc='yiyiya is an os',
)

target('hello')
add_kind("binary")
add_files("./main.c")

```

编译运行

```bash
ya
```