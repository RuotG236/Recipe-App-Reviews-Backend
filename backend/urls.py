"""
URL Configuration for Recipe App Backend
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def api_root(request):
    """API root endpoint with available endpoints info."""
    return JsonResponse({
        'message': 'Welcome to Recipe App API',
        'version': '1.0',
        'endpoints': {
            'auth': {
                'register': '/api/auth/register/',
                'login': '/api/auth/login/',
                'logout': '/api/auth/logout/',
                'refresh': '/api/auth/refresh/',
                'profile': '/api/auth/profile/',
            },
            'recipes': {
                'list': '/api/recipes/',
                'detail': '/api/recipes/{id}/',
                'my_recipes': '/api/recipes/my_recipes/',
                'favorite': '/api/recipes/{id}/favorite/',
                'unfavorite': '/api/recipes/{id}/unfavorite/',
                'rate': '/api/recipes/{id}/rate/',
                'comment': '/api/recipes/{id}/comment/',
            },
            'categories': '/api/categories/',
            'favorites': '/api/favorites/',
            'admin': {
                'users': '/api/admin/users/',
                'recipes': '/api/admin/recipes/',
            }
        }
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('api/', api_root, name='api-info'),
    path('admin/', admin.site.urls),
    path('api/', include('recipes.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)