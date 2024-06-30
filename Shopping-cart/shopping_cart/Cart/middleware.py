class TokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access_token = request.session.get('auth_token')
        if access_token is not None:
            request.META['HTTP_AUTHORIZATION'] = 'Token ' + access_token
        response = self.get_response(request)
        return response