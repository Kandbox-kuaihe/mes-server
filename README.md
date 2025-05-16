# 1. Prerequisites - Software to Install Locally
```
Docker 
VS Code with Python plugin installed 
Node.js 20 or higher
Python 3.12.5 (or install via pyenv install 3.12.5). Special note: Python 3.12.6 or newer is not currently recommended due to potential compatibility issues with the project.
DBeaver or other database connection tools
```




# 1.1 Download Docker Images
```shell

# Skip this step if you can successfully run this command directly (with network access)
docker-compose -f mes-compose.yml -p easy up -d 


# Download images from domestic Dudu Community mirrors 
## For Linux/amd64 (Windows) systems (choose one below):
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/postgres:16.4
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/redis:7.4.1
docker tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/postgres:16.4 postgres:16
docker tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/redis:7.4.1 redis:latest


## For Linux/arm64 (Mac/Linux) systems:
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/postgres:15.3-linuxarm64
docker pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/redis:7.2.4-linuxarm64
docker tag  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/postgres:15.3-linuxarm64 postgres:16
docker tag swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/redis:7.2.4-linuxarm64 redis:latest

```


# 1.2 Copy dev.env
cp .env.template dev.env 

>You can modify environment variables in dev.env as needed


# 1.4 Start Local PG and Redis Services

```shell

# This command will start two Docker containers (PostgreSQL and Redis)
docker-compose -f mes-compose.yml -p easy up -d
# Alternatively if using docker compose (without hyphen):
docker compose -f mes-compose.yml -p easy up -d
# Fallback method if docker-compose is unavailable:
docker run --env-file dev.env -p 5432:5432 -d postgres:16
docker run --env-file dev.env -p 6379:6379 -d redis:latest

# Verify container status and connect to database using DBeaver

```




# 2. Start Backend Service

# 2.1 Environment Setup
> Prerequisite: Install Python plugin in VS Code

```shell
# Create Python virtual environment
python -m venv myenv

# Activate virtual environment
# For Windows: myenv\Scripts\activate
source myenv/bin/activate

```
> In VS Code: Ctrl+Shift+P → "Python: Select Interpreter" → Choose Python 3.12.5


# 2.2 Install Dependencies

```shell
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -e . 

## With Aliyun mirror acceleration:
pip install -e . -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

```




# 2.3 Initialize Database & Import Demo Data

```shell
# In the current directory, execute the over_all.exe file
python tests/over_all.py
```


# 2.4 Start Python Backend Service (Port 8000)
> Via VS Code Run and Debug (Ctrl+Shift+D):
> Select "Web API Server - 8000"   (Or directly execute the command: python -m dispatch.cli server start --host 0.0.0.0 --port 8000 --workers 1 dispatch.main:app)



# 3. Frontend Service

> npm install # or yarn install

# 3.1 Start frontend service

> npm run dev


# 4. Access via Browser
> http://localhost:8881


uvicorn dispatch.main:app --host 0.0.0.0 --port 8000 --workers 1




# 5. Database Migration
```
>mkdir -p  mes/mes_web/src/dispatch/database_util/revisions/tenant/versions


# Schema migrations:
# For tenant schemas (org_code):
      "name": "Server Cli - revision tenant",

      "name": "Server Cli - upgrade - tenant",


# For dispatch_core migrations:


      "name": "Server Cli - revision core",
      "name": "Server Cli - upgrade - core",

# For complete mismatch scenarios:
1. Delete records from alembic_version table in corresponding schema
2. Remove all files in versions folder


```
