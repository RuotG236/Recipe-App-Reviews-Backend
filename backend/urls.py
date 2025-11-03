from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.http import JsonResponse


def home(request):
    return JsonResponse({
        "auth": {
            "register": "/api/auth/register/",
            "login": "/api/auth/login/",
            "refresh": "/api/auth/token/refresh/",
            "logout": "/api/auth/logout/",
        },
        "recipes": {
            "list": "/api/recipes/",
            "detail": "/api/recipes/<id>/",
        },
        "categories": {
            "list": "/api/categories/",
            "detail": "/api/categories/<id>/",
        },
        "admin": "/admin/",
    })


urlpatterns = [
    path("", home),  # root shows all links
    path("admin/", admin.site.urls),
    path("api/", include("recipes.urls")),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
