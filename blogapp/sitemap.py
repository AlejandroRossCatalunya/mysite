from django.contrib.sitemaps import Sitemap

from .models import RSSArticle


class BlogSiteMap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return RSSArticle.objects.filter(published_at__isnull=False).order_by("-published_at")

    def lastmod(self, obj: RSSArticle):
        return obj.published_at