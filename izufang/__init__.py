import os

import celery

# 注册环境变量量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'izufang.settings')

# 创建celery对象   main 为当前包位置，也是指向项目或者app为起始文件位置
# broker 存储消息队列  backend 持久化方式
app = celery.Celery(main='izufang',
                    broker='redis://:Fjl1024.618@8.129.162.35:54321/1',
                    backend='redis://:Fjl1024.618@8.129.162.35:54321/2', )

# 如果从项目的配置文件读取Celery配置信息
app.config_from_object('django.conf:settings')

# 从指定文件读取Celery配置信息
# app.config_from_object('filename')

# 让Celery自动从参数指定的应用中发现异步任务/定时任务
app.autodiscover_tasks(['common', ])
