from rest_framework import serializers

from common.models import *


class DistrictSimpleSerializer(serializers.ModelSerializer):
    '''父级行政简单序列化器'''
    class Meta:
        model = District
        fields = ('distid','name')


class DistrictComplexSerializer(serializers.ModelSerializer):
    '''父级行政序列化器'''
    cities = serializers.SerializerMethodField()
    def get_cities(self, dist):
        queryset = District.objects.filter(parent=dist).only('name',)
        return DistrictSimpleSerializer(queryset, many=True).data

    class Meta:
        model = District
        exclude = ('parent',)


class AgentRetrieveSerializer(serializers.ModelSerializer):
    '''查看单个经理人的详情'''
    estates = serializers.SerializerMethodField()
    @staticmethod
    def get_estates(agent):
        queryset = agent.estates.all().only('name')
        return EstateSimpleSerializer(queryset, many=True).data
    class Meta:
        model = Agent
        fields = '__all__'


class AgentListSerializer(serializers.ModelSerializer):
    '''查看多个经理人的列表'''
    class Meta:
        model = Agent
        fields = ('agentid', 'name', 'tel')


class AgentCreateSerializer(serializers.ModelSerializer):
    '''新增经理人'''
    class Meta:
        model = Agent
        exclude = ('estates',)


class EstateSimpleSerializer(serializers.ModelSerializer):
    '''楼盘简单序列化器'''
    class Meta:
        model = Estate
        fields = ('estateid', 'name')


class  EstateRetrieveSerializer(serializers.ModelSerializer):
    '''楼盘详情序列化器'''
    district = DistrictSimpleSerializer

    class Meta:
        model = Estate
        fields = '__all__'


class HouseTypeSerializer(serializers.ModelSerializer):
    '''户型序列化器'''
    class Meta:
        model = HouseType
        fields = '__all__'

class TagListSerializer(serializers.ModelSerializer):
    '''房源标签序列化器'''
    class Meta:
        model = Tag
        fields = '__all__'

class HouseInfoListSerializer(serializers.ModelSerializer):
    '''房源信息列表序列化器'''
    class Meta:
        model = HouseInfo
        fields = ('houseid', 'title', 'area', 'floor', 'totalfloor', 'price', 'mainphoto', 'street', 'district_level3', 'type')

class HouseInfoRetrieveSerializer(serializers.ModelSerializer):
    '''房源信息详情序列化器'''
    photos = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    type =  HouseTypeSerializer()
    estate = EstateSimpleSerializer()
    agent = AgentRetrieveSerializer()
    tags = TagListSerializer(many=True)

    @staticmethod
    def get_district(houseinfo):
        return DistrictSimpleSerializer(houseinfo.district_level3).data
    @staticmethod
    def get_photos(houseinfo):
        queryset = HousePhoto.objects.filter(house = houseinfo.houseid)
        return HousePhotoSerializer(queryset).data

    class Meta:
        model = HouseInfo
        exclude = ('user', 'district_level2', 'district_level3')


class HouseInfoCreateSerializer(serializers.ModelSerializer):
    '''新增房源信息序列化器'''
    class Meta:
        model = HouseInfo
        exclude = ('type', 'user', 'district_level2', 'district_level3', 'estate', 'agent', 'tags')


class HousePhotoSerializer(serializers.ModelSerializer):
    '''房源图片简单序序列化器'''
    class Meta:
        model = HousePhoto
        fields = ('photoid', 'ismain')