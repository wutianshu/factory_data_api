#!/bin/bash
# 项目主目录
BASE_DIR=/usr/local/work_space/factory_data_api
cd ${BASE_DIR}

# 自动创建日志日志，防止目录不存在时报错
if [ ! -d "factory/logs" ]
then
    mkdir -p factory/logs
fi

# 清除原来的pyc文件
# find ${BASE_DIR} -type f -name *.pyc|xargs rm -f

# 选择对应的虚拟环境
# source ~/.bashrc
workon factory

# 启动python web容器gunicorn
gunicorn -w 1 -b 0.0.0.0:5000 -t 120 --threads 8 factory:app >> factory.log 1>&1 2>&1  &

# 触发后台登陆
sleep 5
curl -s http://127.0.0.1:5000/api/keep-alive >> /dev/null
