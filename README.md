## GIWIFI登录（python实现）

GIWIFI路由器晚上会重启，这导致了电脑掉线的问题，为了解决这部分的校园网认证问题，我用python脚本重写端口，实现校园网的登录认证。

### 介绍 & 目录

```
.\GIWIFI_AUTO_LOGIN             # 主目录
│  .gitignore                   # gitignore文件
│  config.yaml                  # 用户config文件，需要自己手动生成
│  config.yaml.example          # config文件模板
│  main.py                      # 主函数
│  README.md                    # 文档
│  RUN.cmd                      # windows调用入口
│  env.7z                       # 打包的python环境
│  RUN.cmd                      # windows调用入口
└─env                           # python环境，可由env.7z解压得到
```

*请注意：*

第一次运行需要配置yaml.config，并确保网络已经连接至GIWIFI。

yaml.config配置如下，请注意：yaml的空格不能随意删除，所以只需要替换掉<用户名> 和 <密码>即可

```yaml
HOST:
  name: '<用户名>'
  password: '<密码>'
```

### 使用方法

- python3.9 环境下运行main.py（其他版本的我没有测试，不清楚情况）

- 直接运行 RUN.cmd 文件

### 开机启动

由于认证的大部分是windows电脑，没有像 Linux 下 Cron 那么方便的的作业管理系统，因此可以放在开机启动项来解决这个问题。

#### 启动菜单快捷方式

找到
> C:\Users\用户名\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
> 目录并在目录中创建RUN.cmd的快捷方式。

#### 注册表启动项

在以下注册表位置中
> \HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run

添加RUN.cmd为键，RUN.cmd的路径为值的字符串项。

### NO LINK