class ProfesorProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.rol == 'profesor':
            if not hasattr(request.user, 'profesor'):
                Profesor.objects.create(user=request.user)
        return self.get_response(request)