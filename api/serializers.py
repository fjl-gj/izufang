from rest_framework import serializers

from common.models import District


class DistrictSimpleSerializer(serializers.ModelSerializer):
    '''父级行政简单序列化器'''
    class Meta:
        model = District
        fields = ('distid','name')

class DistrictComplexSerializer(serializers.ModelSerializer):
    '''父级行政简单序列化器'''
    cities = serializers.SerializerMethodField()
    def get_cities(self, dist):
        queryset = District.objects.filter(parent=dist).only('name',)
        return DistrictSimpleSerializer(queryset, many=True).data

    class Meta:
        model = District
        exclude = ('parent',)