from django.contrib import admin
from django.urls import path
from user_login.views import login_view, refresh_token_view, logout_view, sign_up, change_password


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='token_obtain_pair'),
    path('refreshtoken/', refresh_token_view, name='token_refresh'),
    path('logout/', logout_view, name='logout'),
    path('signup/', sign_up, name='sign_up'),
    path('change_password/', change_password, name='change_password'),

]
