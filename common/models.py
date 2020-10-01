# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class District(models.Model):
    '''省市区地区'''
    # 地区ID
    distid = models.IntegerField(primary_key=True)
    # 自参照 对象模型 ForeignKey,db_column对应数据库表字段  父级行政区域（省级行政区域的父级为None）
    parent = models.ForeignKey(to='self', on_delete=models.DO_NOTHING, db_column='pid', blank=True, null=True)
    # 地区名称
    name = models.CharField(max_length=255)
    # 修改为布尔对象 默认 False 不热门
    ishot = models.BooleanField(default=False)
    intro = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tb_district'


class Agent(models.Model):
    '''经理人'''
    # 经理人ID
    agentid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    tel = models.CharField(max_length=20)
    # 经理人服务星级
    servstar = models.IntegerField()
    # 经理人提供的房源真实度
    realstar = models.IntegerField()
    # 经理人业务水平
    profstar = models.IntegerField()
    # 经理人是否持有专业认证
    certificated = models.IntegerField()
    # 经理人负责的楼盘
    # 多对多关联，经理人对应楼盘 数据库中没有对应的表，增加中间表AgentEstat 关联多对多 ManyToMany 对象模型
    estates = models.ManyToManyField(to='Estate', through='AgentEstat')

    class Meta:
        managed = False
        db_table = 'tb_agent'

class Estate(models.Model):
    '''楼盘'''
    estateid = models.AutoField(primary_key=True)
    # 关联行政区域 转对象模型
    district = models.ForeignKey(to=District, on_delete=models.DO_NOTHING, db_column='distid')
    name = models.CharField(max_length=255)
    # 楼盘热度
    hot = models.IntegerField(blank=True, null=True)
    intro = models.CharField(max_length=511, blank=True, null=True)
    # 写上多对多关联，经理人对应楼盘 数据库中没有对应的表，增加中间表AgentEstat 关联多对多 ManyToMany 对象模型
    agents = models.ManyToManyField(to='Agent', through='AgentEstate')

    class Meta:
        managed = False
        db_table = 'tb_estate'


class AgentEstate(models.Model):
    '''经理人与楼盘中间体'''
    agent_estate_id = models.AutoField(primary_key=True)
    agent = models.ForeignKey(to='Agent', on_delete=models.DO_NOTHING, db_column='agentid')
    estate = models.ForeignKey(to='Estate', on_delete=models.DO_NOTHING, db_column='estateid')

    class Meta:
        managed = False
        db_table = 'tb_agent_estate'
        unique_together = (('agent', 'estate'),)


class User(models.Model):
    '''用户'''
    userid = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=20)
    password = models.CharField(max_length=32)
    realname = models.CharField(max_length=20)
    sex = models.IntegerField(blank=True, null=True)
    tel = models.CharField(unique=True, max_length=20)
    email = models.CharField(unique=True, max_length=255, blank=True, null=True)
    # 用户注册日期
    regdate = models.DateTimeField(blank=True, null=True)
    # 用户积分
    point = models.IntegerField(blank=True, null=True)
    # 用户最后登录日期时间
    lastvisit = models.DateTimeField(blank=True, null=True)
    # 多对多关系 与角色关联多对多
    roles = models.ManyToManyField(to='Role', through='UserRole')

    class Meta:
        managed = False
        db_table = 'tb_user'


class HouseType(models.Model):
    '''户型'''
    typeid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'tb_house_type'


class HouseInfo(models.Model):
    '''房源信息'''
    houseid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    # 面积
    area = models.IntegerField()
    # 楼层
    floor = models.IntegerField()
    # 总楼层
    totalfloor = models.IntegerField()
    # 朝向
    direction = models.CharField(max_length=10)
    # 价格
    price = models.IntegerField()
    # 元/月 单位
    priceunit = models.CharField(max_length=10)
    # 房源环境描述
    detail = models.CharField(max_length=511, blank=True, null=True)
    # 照片主图
    mainphoto = models.CharField(max_length=255)
    # 房源发布日期
    pubdate = models.DateField()
    # 街道地址
    street = models.CharField(max_length=255)
    # 靠近地铁  布尔值
    hassubway = models.BooleanField(default=False)
    # 是否合租  shared共享 布尔值
    isshared = models.BooleanField(default=False)
    # 是否有中介费
    hasagentfees = models.BooleanField(default=False)
    # 类型id
    type = models.ForeignKey(to=HouseType, on_delete=models.DO_NOTHING, db_column='typeid')
    # 用户id 转对象模型
    user = models.ForeignKey(to=User, on_delete=models.DO_NOTHING, db_column='userid')
    # 二级行政区域
    dist_level2 = models.ForeignKey(to=District, on_delete=models.DO_NOTHING, db_column='distid2')
    # 三级行政区域
    dist_level3 = models.ForeignKey(to=District, on_delete=models.DO_NOTHING, db_column='distid3')
    # 楼盘
    estate = models.ForeignKey(to=Estate, on_delete=models.DO_NOTHING, db_column='estateid', blank=True, null=True)
    # 经理人
    agent = models.ForeignKey(to=Agent, on_delete=models.DO_NOTHING, db_column='agentid', blank=True, null=True)
    # 标签
    tags = models.ManyToManyField(to='Tag', through='HouseTag')

    class Meta:
        managed = False
        db_table = 'tb_house_info'


class Tag(models.Model):
    '''标签'''
    tagid = models.AutoField(primary_key=True)
    content = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'tb_tag'


class HousePhoto(models.Model):
    '''房源照片'''
    photoid = models.AutoField(primary_key=True)
    # 房子id信息
    house = models.ForeignKey(to='HouseInfo', on_delete=models.DO_NOTHING, db_column='houseid')
    # 照片存储路径
    path = models.CharField(max_length=255)
    # 主图
    ismain = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'tb_house_photo'


class HouseTag(models.Model):
    '''房屋标签'''
    house_tag_id = models.AutoField(primary_key=True)
    house = models.ForeignKey(to='HouseInfo', on_delete=models.DO_NOTHING, db_column='houseid')
    # 房源信息
    tag = models.ForeignKey(to='Tag', on_delete=models.DO_NOTHING, db_column='tagid')

    class Meta:
        managed = False
        db_table = 'tb_house_tag'
        unique_together = (('house', 'tag'),)


class Record(models.Model):
    '''记录'''
    recordid = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(to='User', on_delete=models.DO_NOTHING, db_column='userid')
    house = models.ForeignKey(to='HouseInfo', on_delete=models.DO_NOTHING, db_column='houseid')
    # 记录时间
    recorddate = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tb_record'
        unique_together = (('userid', 'houseid'),)


class LoginLog(models.Model):
    '''登录信息'''
    logid = models.BigAutoField(primary_key=True)
    # 用户id
    user = models.ForeignKey(to='User', on_delete=models.DO_NOTHING, db_column='userid')
    # 用户ip
    ipaddr = models.CharField(max_length=255)
    # 用户登陆时间
    logdate = models.DateTimeField(blank=True, null=True)
    # 用户登录设备编码
    devcode = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tb_login_log'


class Privilege(models.Model):
    '''权限'''
    privid = models.AutoField(primary_key=True)
    # 权限方式
    method = models.CharField(max_length=15)
    # 接口数据url路由地址
    url = models.CharField(max_length=1024)
    # 角色权限
    detail = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tb_privilege'


class Role(models.Model):
    '''角色'''
    roleid = models.AutoField(primary_key=True)
    rolename = models.CharField(max_length=255)
    privs = models.ManyToManyField(to='Privilege', through='RolePrivilege')

    class Meta:
        managed = False
        db_table = 'tb_role'


class RolePrivilege(models.Model):
    '''角色权限中间体'''
    role_priv_id = models.AutoField(primary_key=True)
    # 角色
    role = models.ForeignKey(to=Role, on_delete=models.DO_NOTHING ,db_column='roleid')
    # 权限
    privileges = models.ForeignKey(to=Privilege, on_delete=models.DO_NOTHING, db_column='privid')

    class Meta:
        managed = False
        db_table = 'tb_role_privilege'
        unique_together = (('role', 'privileges'),)


class UserRole(models.Model):
    '''用户角色中间体'''
    user_role_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(to='User', on_delete=models.DO_NOTHING, db_column='userid')
    role = models.ForeignKey(to='Role', on_delete=models.DO_NOTHING, db_column='roleid')

    class Meta:
        managed = False
        db_table = 'tb_user_role'
        unique_together = (('user', 'role'),)
