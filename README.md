# JMHelper - 漫画下载与转换 NoneBot2 插件

适用于 NoneBot2 的 JM(禁漫天堂) 插件，支持搜索关键词、下载指定漫画并上传群文件、查看漫画元信息等功能。

## 效果展示

### 漫画元信息查询

![漫画元信息查询效果图1](/docs/screenshot/jmt1.png)
![漫画元信息查询效果图2](/docs/screenshot/jmt2.png)

## 漫画搜索

![漫画搜索效果图](/docs/screenshot/jms1.png)
![漫画搜索效果图](/docs/screenshot/jms2.png)

### 漫画下载

![漫画下载效果图](/docs/screenshot/jm1.png)

## 安装方法

```bash
git clone https://github.com/X-Zero-L/jmhelper.git
```

或者使用 git 子模块

```bash
git submodule add https://github.com/X-Zero-L/jmhelper.git path/to/plugins/jmhelper
```

- 如果你使用 uv, 请使用以下命令

```bash
uv add -r path/to/plugins/jmhelper/requirements.txt
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
- `dir_rule.base_dir`: 设置下载和 PDF 输出的根目录, 注意和`pdf_dir`保持一致

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

# 插件的配置示例
plugins:
  after_photo:
    # 把章节的所有图片合并为一个pdf的插件
    # 使用前需要安装依赖库: [pip install img2pdf]
    - plugin: img2pdf
      kwargs:
        pdf_dir: /your/path/to/download # pdf存放文件夹，和dir_rule.base_dir保持一致
        filename_rule: Pid # pdf命名规则，P代表photo, id代表使用photo.id也就是章节id

  after_album:
    # img2pdf也支持合并整个本子，把上方的after_photo改为after_album即可。
    # https://github.com/hect0x7/JMComic-Crawler-Python/discussions/258
    # 配置到after_album时，需要修改filename_rule参数，不能写Pxx只能写Axx示例如下
    - plugin: img2pdf
      kwargs:
        pdf_dir: /your/path/to/download # pdf存放文件夹，和dir_rule.base_dir保持一致
        filename_rule: Aid # pdf命名规则，A代表album, id代表使用album.id也就是本子id
```

- 配置项详情请看 jmcomic 项目的[文档](https://jmcomic.readthedocs.io/zh-cn/latest/)
- 如果你使用 docker 部署 nonebot/llonebot/napcat 等，建议这里的下载目录都对等挂载，不然你只能自己修改插件代码了 🤭
- 本插件每天凌晨 3 点会清理今天之前的下载文件，所以请保证您输入的下载目录仅用于 jm 资源的下载，如果您不希望清理文件，请在环境变量中设置`JM_CLEAN=False`

## 使用方法

插件注册了以下指令：

- `/jm [漫画ID]` - 下载并转换指定 ID 的漫画，上传 PDF 文件
- `/jmt [漫画ID]` - 查看指定 ID 的漫画元信息，如标题、作者、标签等
- `/jms [关键词]` - 搜索漫画，返回搜索结果

示例：

```
/jm 123456
/jmt 123456
/jms genshin
```

## 注意事项

1. 请确保配置了正确的代理设置，否则可能无法访问资源
2. 确保机器人有上传群文件的权限
3. 部分敏感内容需要在`option.yml`中配置 cookies 才能下载
4. 请合理使用，避免频繁请求造成服务器压力
5. 虽然本插件使用了`nonebot_plugin_alconna`,但是文件上传接口使用的是 onebot11 的，所以不支持其他协议 😀
6. 如果你需要日志记录，请看[logfire](https://logfire.pydantic.dev/docs/)

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
