from django_filters import filterset
from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.response import Response

from common.models import Estate, HouseInfo


class CustomPagination(PageNumberPagination):
    '''自定义分页'''
    page_size_query_param = 'size'
    max_page_size = 20


class AgentCursorPagination(CursorPagination):
    """经理人游标分页类"""
    page_size_query_param = 'size'
    max_page_size = 50
    ordering = '-agentid'


class EstateFilterSet(filterset.FilterSet):
    """自定义楼盘筛选器"""
    name = filterset.CharFilter(lookup_expr='contains')
    minhot = filterset.NumberFilter(field_name='hot', lookup_expr='gte')
    maxhot = filterset.NumberFilter(field_name='hot', lookup_expr='lte')
    dist = filterset.NumberFilter(field_name='district')

    class Meta:
        model = Estate
        fields = ('name', 'minhot', 'maxhot', 'dist')


class HouseInfoFilterSet(filterset.FilterSet):
    """自定义房源筛选器"""
    title = filterset.CharFilter(lookup_expr='contains')
    minprice = filterset.NumberFilter(field_name='price', lookup_expr='gte')
    maxprice = filterset.NumberFilter(field_name='price', lookup_expr='lte')
    minarea = filterset.NumberFilter(field_name='area', lookup_expr='gte')
    maxarea = filterset.NumberFilter(field_name='area', lookup_expr='lte')
    district = filterset.NumberFilter(method='filter_by_district')

    @staticmethod
    def filter_by_district(queryset, name, value):
        return queryset.filter(Q(district_level2=value) |
                               Q(district_level3=value))

    class Meta:
        model = HouseInfo
        fields = ('title', 'minprice', 'maxprice', 'minarea', 'maxarea', 'type', 'district')


class DefaultResponse(Response):
    '''响应重写'''
    def __init__(self, code=100000, hint='操作成功', data=None, status=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None):
        _data = {'code': code, 'hint': hint}
        if data:
            _data.update(data)
        super().__init__(data=None, status=None,template_name=None, headers=None,exception=False, content_type=None)
