from datetime import datetime

from django.shortcuts import render


def set_useragent_on_request_middleware(get_response):
    def middleware(request):
        request.user_agent = request.META["HTTP_USER_AGENT"]
        response = get_response(request)
        return response

    return middleware

class CountRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request):
        self.requests_count += 1
        response = self.get_response(request)
        self.responses_count += 1
        return response

    def process_exception(self, request, exception):
        self.exceptions_count += 1


class ThrottlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.ips = dict()

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        if ip in self.ips.keys():
            self.ips[ip]["count"] += 1
            delta = datetime.now() - min(self.ips[ip]["last"])
            if self.ips[ip]["count"] % 5 == 0 and delta.seconds < 4:
                context = {"ip": ip, "count": self.ips[ip]["count"]}
                return render(request, "requestdataapp/ip-delay.html", context=context)
            else:
                self.ips[ip]["last"][self.ips[ip]["count"] % 5] = datetime.now()

        else:
            self.ips[ip] = {"count": 1, "last": [datetime.now()] * 5}
        return self.get_response(request)
