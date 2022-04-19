# Flog

一个根据规则集来处理文本日志的工具。

## 前言

在日常开发过程中，由于缺乏必要的日志规范，导致很多人乱打一通，一个日志文件夹解压缩后往往有几十万行。

日志泛滥会导致信息密度骤减，给排查问题带来了不小的麻烦。

以前都是用`grep`之类的工具先挑选出有用的，再逐条进行排查，费时费力。在忍无可忍之后决定写这个工具，根据规则自动分析日志、剔除垃圾信息。

## 使用方法

### 安装

```shell
python setup.py install
```

### 基础用法

```shell
flog -r rules.yaml /path/to/your.log -o /path/to/filtered.log
```

其中：
- `rules.yaml`是规则文件
- `/path/to/your.log`是原始的日志文件
- `/path/to/filtered.log`是过滤后的日志文件

## 规则语法

### 基础

```yaml
- name: Rule Name #规则集名称
- patterns: #规则列表
    # 如果匹配到 ^Hello，就输出 Match Hello
    - match: "^Hello"
      message: "Match Hello"
    
    # 多行模式，以^Hello开头，以^End结束
    - start: "^Hello"
      end: "^End"
      message: "Match Hello to End"

    - start: "Start"
      start_message: "Match Start" #匹配开始时显示的信息
      end: "End"
      end_messagee: "Match End" #结束时显示的信息
```

纯过滤模式

```yaml
- name: Rule Name
- patterns:
    - match: "^Hello" #删除日志中以Hello开头的行
    - start: "^Hello" #多行模式，删除从Hello到End中间的所有内容
      end: "^End"
```

过滤日志内容，并输出信息

```yaml
- name: Rule Name
- patterns:
    - match: "^Hello" #删除日志中以Hello开头的行
      message: "Match Hello"
      action: drop # drop：删除此行日志，bypass：保留此行日志（如果有message字段，默认为bypass；如果没有message字段，默认为drop）
```

### message

`message` 字段用于在标准输出显示信息，并且支持[jinja2](https://jinja.palletsprojects.com/en/3.1.x/)模版语法来自定义输出信息内容，通过它可以实现一些简单的日志分析功能。

目前支持的参数有:

- `lines`: （多行模式下）匹配到的所有行
- `content`: 匹配到的日志内容
- `captures`: 正则表达式（`match`/`start`/`end`）捕获的内容

例如：

```yaml
- name: Rule Name
- patterns:
    - match: "^Hello (.*)"
      message: "Match {{captures[0]}}"
```

如果遇到："Hello lilei"，则会在终端输出"Match lilei"

## License

MIT