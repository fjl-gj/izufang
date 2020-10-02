from rest_framework.pagination import PageNumberPagination, CursorPagination


class CustomPagination(PageNumberPagination):
    '''自定义分页'''
    page_size_query_param = 'size'
    max_page_size = 20


class AgentCursorPagination(CursorPagination):
    '''自定义经理人分页'''
    page_size_query_param = 'size'
    max_page_size = 20
    ordering = '-agentid'