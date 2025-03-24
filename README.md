# JMHelper - 漫画下载与转换 NoneBot2 插件

适用于 NoneBot2 的 JM 下载插件，支持下载并转换为 PDF 格式。

## 安装方法

```bash
git clone https://github.com/X-Zero-L/jmhelper.git
cd jmhelper
uv sync
```

- 如果你不知道 uv 是什么，请查看 [uv](https://github.com/astral-sh/uv)
- 如果你不想使用 uv，那么你可以使用以下命令

```bash
pip install -r requirements.txt
```

## 配置说明

1. 复制插件目录中的`option.example.yml`为`option.yml`：

```bash
cp option.example.yml option.yml
```

2. 编辑`option.yml`文件，修改以下关键配置：

- `client.postman.meta_data.proxies`: 设置代理（必须，不然可能无法访问）
- `dir_rule.base_dir`: 设置下载和 PDF 输出的根目录

主要配置项解释：

```yaml
client:
  impl: html # 客户端实现，html(网页端)或api(APP端)
  domain: # 可用域名列表
    - 18comic.vip
    - 18comic.org
  postman:
    meta_data:
      proxies: 127.0.0.1:7890 # 代理设置，根据你的环境修改

download:
  cache: true # 是否启用缓存
  image:
    decode: true # 是否解码图片
    suffix: .jpg # 图片格式

dir_rule:
  base_dir: /your/path/to/download # 下载根目录，必须修改
  rule: Bd_Ptitle # 目录结构规则
```

- 其他配置项看 jmcomic 项目的[文档](https://jmcomic.readthedocs.io/zh-cn/latest/)
- 如果你使用 docker 部署 nonebot/llonebot/napcat 等，建议这里的下载目录都对等挂载，不然你只能自己修改插件代码了

## 使用方法

插件注册了以下指令：

- `/jm [漫画ID]` - 下载并转换指定 ID 的漫画
- 别名：`下载漫画`、`下载本子`、`/JM`、`/Jm`、`/jM`

示例：

```
/jm 123456
```

机器人将下载漫画并转换为 PDF，完成后会在群文件中上传 PDF 文件。

## 注意事项

1. 请确保配置了正确的代理设置，否则可能无法访问资源
2. 确保机器人有上传群文件的权限
3. 部分敏感内容需要在`option.yml`中配置 cookies 才能下载
4. 请合理使用，避免频繁请求造成服务器压力
5. 虽然本插件使用了`nonebot_plugin_alconna`,但是文件上传接口使用的是 onebot11 的，所以不支持其他协议 😀

## 目录结构

```
jmhelper/
├── __init__.py          # 插件主入口
├── config.py            # 配置定义
├── converter.py         # PDF转换器
├── downloader.py        # 下载器
├── utils.py             # 工具函数
└── option.example.yml   # 配置示例
```
