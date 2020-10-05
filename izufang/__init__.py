import celery


# 创建celery对象 指定持久化方式和模块名消息代理
app = celery.Celery('izufang',
                    backend='redis://:Fjl1024.618@8.129.162.35:54321/1',
                    broker='redis://:Fjl1024.618@8.129.162.35:54321/2')

app.autodiscover_tasks(['common', ])