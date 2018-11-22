from django.urls import path
from . import views
from .feeds import LastestPostFeed

app_name = 'blog'
urlpatterns = [
    # path('', views.ListView.as_view(), name='list'),
    path('', views.post_list, name='list'),
    path('tag/<slug:tag_slug>/', views.post_list, name='list_by_tag'),
    path('<int:pk>/', views.post_detail, name='detail'),
    path('<int:pk>/share/', views.post_share, name='share'),
    path('feed/', LastestPostFeed(), name='post_feed'),
]
