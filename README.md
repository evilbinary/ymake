# ymake
ymake is a make dsl build tools


## 安装

```bash
pip install yymake
```

## 使用

```python
from ymake.yaya import *


project("yiyiya",
    version='12.0',
    desc='yiyiya is an os',
)

add_subs('./**/*.py')

process()

```