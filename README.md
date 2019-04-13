# 堆糖头像采集

堆糖头像采集 threadpool + redis 根据 md5 检验不重复的采集头像 , 并根据点赞数量排序生成报告文件

+ 环境引用
> Anaconda 2019.3 (Python3.7.3)

> Redis 3.0.2 Windows

+ 第三方库使用（请使用 pip安装）

```bash
pip install requests
pip install redis
pip install threadpool
```

## 运行

```bash
python run.py
```

输入图片保存的路径后回自动运行

## 结束

采集结束后会显示 <b>completed</b> 字样, 随后会在图片保存路径生成一个 <b>report.txt</b> 的文件, 根据用户喜欢数对头像进行排序