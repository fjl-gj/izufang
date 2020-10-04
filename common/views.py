from django.http import HttpResponse
from django.shortcuts import redirect



def show_index(request):
    return redirect('/static/html/index.html')


# def get_captcha(request):
#     '''验证码'''
#     instance = Captcha.instance()
#     text = gen_captcha_text()
#     data = instance.generate(text)
#     return HttpResponse(data, content_type='image/png')