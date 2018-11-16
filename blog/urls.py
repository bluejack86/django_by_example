from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    # path('', views.ListView.as_view(), name='list'),
    path('', views.post_list, name='list'),
    path('<int:pk>/', views.post_detail, name='detail'),
    path('<int:pk>/share/', views.post_share, name='share'),
]
