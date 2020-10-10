import openpyxl
from django.http import HttpResponse
from django.shortcuts import redirect


def show_index(request):
    return redirect('/static/html/index.html')


def export_excel(request):
    wb = openpyxl.Workbook()