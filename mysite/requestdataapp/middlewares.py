from django.http import HttpRequest
import time
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

def setup_useragent_on_request_middleware(get_response):

    print("initial call")

    def middleware(request: HttpRequest):
        print("before get response")
        request.user_agent = request.META["HTTP_USER_AGENT"]
        response = get_response(request)
        print("after get response")
        return response

    return middleware

class CountRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request: HttpRequest):
        self.requests_count += 1
        print("requests count", self.requests_count)
        response = self.get_response(request)
        self.responses_count +=1
        print("responses count", self.responses_count)
        return response

    def process_eeception(self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1
        print("got", self.exceptions_count, "exceptions so far")

class ThrottlingMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_times = {} # {ip_address: last_request_time}
        self.throttle_delay = 10 # seconds

    def __call__(self, request):
        ip_address = self.get_client_ip(request)
        current_time = time.time()

        if ip_address in self.request_times:
            last_request_time = self.request_times[ip_address]
            time_diff = current_time - last_request_time
            if time_diff < self.throttle_delay:
                return HttpResponseForbidden(
                    f"Too many requests. Please wait {self.throttle_delay - time_diff:.2f} seconds."
                )

        self.request_times[ip_address] = current_time
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip