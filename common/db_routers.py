'''
官方文档操作
Url：https://docs.djangoproject.com/zh-hans/2.2/topics/db/multi-db/#topics-db-multi-db-routing
'''

import random


class MasterSlaveRouter:
    @staticmethod
    def db_for_read(model, **hints):
        """
        Reads go to a randomly-chosen replica.
        """
        # 这里判断选择的是默认的还是other其他实例的数据库操作
        if model._meta.app_label == '':
            return 'other'
        return random.choice(['slave1', ])

    @staticmethod
    def db_for_write(model, **hints):
        """
        Writes always go to primary.
        """
        # 这里判断选择的是默认的还是other其他实例的数据库操作
        if model._meta.app_label == '':
            return 'other'
        return 'default'

    @staticmethod
    def allow_relation(obj1, obj2, **hints):
        return None

    @staticmethod
    def allow_migrate(db, app_label, model_name=None, **hints):
        return True
