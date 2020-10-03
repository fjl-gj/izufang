from django_filters import filterset
from rest_framework.pagination import PageNumberPagination, CursorPagination

from common.models import Estate, HouseInfo


class CustomPagination(PageNumberPagination):
    '''自定义分页'''
    page_size_query_param = 'size'
    max_page_size = 20


class AgentCursorPagination(CursorPagination):
    '''自定义经理人分页'''
    page_size_query_param = 'size'
    max_page_size = 20
    ordering = '-agentid'


class EstateFilterSet(filterset.FilterSet):
    '''自定义楼盘筛选'''
    name = filterset.CharFilter(lookup_expr='startswith')
    minhot = filterset.NumberFilter(field_name='hot', lookup_expr='gte')
    mixhot = filterset.NumberFilter(field_name='hot', lookup_expr='lte')
    dist = filterset.NumberFilter(field_name='district')
    class Meta:
        model = Estate
        fields = ('name', 'minhot', 'mixhot', 'dist')

class HouseInfoFilterSet(filterset.FilterSet):
    minarea = filterset.NumberFilter(field_name='area', lookup_expr='gte')
    mixarea = filterset.NumberFilter(field_name='area', lookup_expr='lte')
    floor = filterset.NumberFilter()
    minprice = filterset.NumberFilter(field_name='price', lookup_expr='gte')
    mixprice = filterset.NumberFilter(field_name='price', lookup_expr='lte')
    pubdate = filterset.CharFilter()
    class Meta:
        model = HouseInfo
        fields = ('minarea', 'mixarea', 'floor', 'minprice', 'mixprice', 'pubdate')