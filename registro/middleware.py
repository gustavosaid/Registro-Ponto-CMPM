from django.shortcuts import render
from django.http import HttpResponseNotFound , HttpResponseForbidden

class Force404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Se a resposta for erro 404, renderiza a página personalizada
        if response.status_code == 404:
            return render(request, '404.html', status=404)

        return response

class BlockIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.blocked_ips = [
            '179.211.254.37',
            '206.168.34.92',
            '52.167.144.54',
            '104.248.82.172',
            '157.55.39.225',
            '40.77.167.59',
            '167.94.146.50',
            '47.245.103.18', 
            '64.226.120.42',
            '146.70.116.227',
            '162.216.150.150',
            '161.35.190.246',
            '165.227.43.174',
            '148.113.193.79',
            '101.36.121.22',
            '66.249.66.160',
            '119.96.25.158',
            '179.126.219.143'
            '167.94.145.110',
            '87.236.176.32',
            '162.216.150.133',
            '164.90.193.142',
            '167.94.138.40',
            '64.227.146.243',
            
        ]

    def __call__(self, request):
        ip = self.get_client_ip(request)
        print(f"IP recebido: {ip}")  # Debug opcional
        if ip in self.blocked_ips:
            print(f"Bloqueando IP: {ip}")  # Debug opcional
            return render(request,'404.html')
            #return HttpResponseForbidden("Access denied.")
        return self.get_response(request)

    def get_client_ip(self, request):
        # Usa X-Forwarded-For se estiver atrás de proxy (como nginx)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
