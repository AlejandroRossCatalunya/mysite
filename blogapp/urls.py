from django.urls import path, include
from .views import ArticlesListView, RSSArticlesListView, RSSArticlesDetailView, LatestArticlesFeed


app_name = "blogapp"

urlpatterns = [
    path("list/", ArticlesListView.as_view(), name="article_list"),
    path("articles/", RSSArticlesListView.as_view(), name="articles"),
    path("articles/<int:pk>/", RSSArticlesDetailView.as_view(), name="article"),
    path("articles/latest/feed/", LatestArticlesFeed(), name="articles-feed")
    ]