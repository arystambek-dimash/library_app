from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('api.users.urls')),
    path('books/', include('api.books.urls')),
    path('networks/', include('api.networks.urls'))
]
