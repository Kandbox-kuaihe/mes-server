# 1. 前期准备-本地需要安装的软件
```
Docker 
VS code 并安装 python 插件 
node js 20或以上
Python 3.12.5 (或者 pyenv install 3.12.5)。 请特别注意暂时不推荐使用 Python 3.12.6 或更高版本的 Python，因为更高的 Python 版本可能和当前项目存在兼容性问题。
Dbeaver 等数据库连接工具
```




# 1.1 下载 docker  镜像包
```shell

# 如果你的电脑直接运行这个命令成功的话（可以翻墙下载的话），这一步的步骤可以跳过 
docker-compose -f mes-compose.yml -p easy up -d 


# 下载的是国内 渡渡鸟 社区的镜像 
## 如果你的电脑是 linux/amd64 （windows） 的话，可以运行这个 (跟下面的二选一)
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/postgres:16.4
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/redis:7.4.1
docker tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/postgres:16.4 postgres:16
docker tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/redis:7.4.1 redis:latest


## 如果你的电脑是 Linux/arm64 (mac or linux )的话，可以运行这个
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/postgres:15.3-linuxarm64
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/redis:7.2.4-linuxarm64
docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/postgres:15.3-linuxarm64 postgres:16
docker tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/redis:7.2.4-linuxarm64 redis:latest

```


# 1.2 拷贝 dev.env
cp .env.template dev.env 

>dev.env 环境变量文件可以自行修改


# 1.4 本地启动 pg,redis 服务

```shell

# 此条命令会启动两个 docker 容器 ，pgsql 和redis 
docker-compose -f mes-compose.yml -p easy up -d  或者 docker compose -f mes-compose.yml -p easy up -d
# 如果本地没有 docker-compose ，也可以执行这个 
docker run --env-file dev.env -p 5432:5432 -d postgres:16
docker run --env-file dev.env -p 6379:6379 -d redis:7.4.1

# 执行完查看 容器是否成功启动， dbeaver 连接数据库看是否正常 

```




# 2. 启动后端服务 

# 2.1 环境准备
> 前提： vscode 安装 Python插件

```shell
# 创建新的python虚拟环境（推荐）
python -m venv myenv

# 激活并进入虚拟环境
source myenv/bin/activate

```
> 前提： vscode，ctrl + shift + P  , 选中 Python: Select Interpreter, 选择对应的Python 3.12.5 


# 2.2 安装依赖包

```shell
# 升级PIP 
pip install --upgrade pip

# 安装 依赖
pip install -e . 

## 或者使用阿里云加速
pip install -e . -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

```




# 2.3 启动 数据库初始化，并且导入demo数据

```shell
# 在当前目录下，执行 over_all.py文件
python tests/over_all.py
```


# 2.4 运行 Python后端 服务 8000 端口
> 找到 侧边栏Run and Debug (Ctrt + Shift + D)
> 运行命令 Web API Server - 8000   (或者直接执行命令: python -m dispatch.cli server start --host 0.0.0.0 --port 8000 --workers 1 dispatch.main:app)



# 3. 前端服务

> npm install 或 yarn install 

# 3.1 启动前端服务

> npm run dev


# 4. 浏览器访问
> http://localhost:8881


uvicorn dispatch.main:app --host 0.0.0.0 --port 8000 --workers 1




# 5. 数据库迁移问题
```
>mkdir -p  mes/mes_web/src/dispatch/database_util/revisions/tenant/versions


# 运行下面脚本
# org_code 下面的 shema 迁移 
      "name": "Server Cli - revision tenant",

      "name": "Server Cli - upgrade - tenant",


# dispatch_core 迁移 


      "name": "Server Cli - revision core",
      "name": "Server Cli - upgrade - core",

 完全对不上号的情况下 ,
 删除对应 shema 下的 alembic_version 表 数据 , 删除对应versions 文件夹下的所有文件


```
