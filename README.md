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

add_subs('./**/*.py')

```

编译运行

```bash
ya
```