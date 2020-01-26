# QQ机器人-疫情数据查询
## 插件简介
基于nonebot，使用python开发的酷Q机器人插件，实现实时的疫情数据查询。  
国家级数据来自[腾讯新闻](https://news.qq.com/zt2020/page/feiyan.htm)，省市级数据来自[丁香园](https://3g.dxy.cn/newh5/view/pneumonia)

## 环境
* python 3.7
* nonebot 1.3.1
* CoolQ HTTP API 4.13.0

## 安装依赖
```shell script
pip3 install -r requirement.txt
```

## 运行脚本
```shell script
python bot.py
```
出现类似如下内容则运行成功 
```text
ujson module not found, using json  
msgpack not installed, MsgPackSerializer unavailable  
[2020-01-26 12:12:33,769 nonebot] INFO: Succeeded to import "plugins.2019nCoV"  
[2020-01-26 12:12:33,769 nonebot] INFO: Running on 0.0.0.0:8099  
Running on https://0.0.0.0:8099 (CTRL + C to quit)  
[2020-01-26 12:12:33,769] ASGI Framework Lifespan error, continuing without Lifespan support  
```
