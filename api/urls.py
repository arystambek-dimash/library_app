from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.url')),
    path('books/', include('books.url')),
    path('socials/', include('socials.urls'))
]
