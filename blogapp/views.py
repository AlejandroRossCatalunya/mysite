from django.views.generic import ListView, DetailView
from django.contrib.syndication.views import Feed
from django.urls import reverse, reverse_lazy

from .models import Article, RSSArticle


class ArticlesListView(ListView):
    """
    ListView отображает список статей
    """
    template_name = "blogapp/article_list.html"
    context_object_name = "articles"
    queryset = Article.objects.select_related("author", "category").prefetch_related("tags").defer("content", "author__bio")


class RSSArticlesListView(ListView):
    queryset = RSSArticle.objects.filter(published_at__isnull=False).order_by("-published_at")


class RSSArticlesDetailView(DetailView):
    model = RSSArticle


class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on changes and addition blog articles"
    link = reverse_lazy("blogapp:articles")

    def items(self):
        return RSSArticle.objects.filter(published_at__isnull=False).order_by("-published_at")[:5]

    def item_title(self, item: RSSArticle):
        return item.title

    def item_description(self, item: RSSArticle):
        return item.body[:200]

    def item_link(self, item: RSSArticle):
        return reverse("blogapp:article", kwargs={"pk": item.pk})