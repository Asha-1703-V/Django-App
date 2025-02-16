from timeit import default_timer

from django.http import HttpResponse, HttpRequest
from django.shortcuts import render


def shop_index(request: HttpRequest):
    context = {
        "time_running": default_timer(),

    }
    return render(request, 'shopapp/shop-index.html', context=context)