from django.contrib import admin
from django.urls import path
from .views import  about, privacy, home
from .views import HomeView
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home', HomeView.as_view(), name='home'),
    path('', home, name='h'),
    path('about/', about, name='about'),
    path('privacy/', privacy, name='privacy'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'Who_U_R.views.custom_404'
handler500 = 'Who_U_R.views.custom_500'