from django.http import HttpResponse, HttpRequest
from django.shortcuts import render


def shop_index(request: HttpRequest):
    print(request.path)
    print(request.method)
    print(request.headers)
    return HttpResponse("<h1>Hello World!<h1>")