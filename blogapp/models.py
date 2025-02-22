from django.db import models
from django.urls import reverse


class Author(models.Model):
    """
    Модель Author представляет автора статьи.
    """
    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"
    name = models.CharField(max_length=100, db_index=True)
    bio = models.TextField(null=False, blank=True)


class Category(models.Model):
    """
    Модель Category представляет категорию статьи.
    """
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
    name = models.CharField(max_length=40, db_index=True)


class Tag(models.Model):
    """
    Модель Tag представляет тэг, который можно назначить статье.
    """
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
    name = models.CharField(max_length=20, db_index=True)


class Article(models.Model):
    """
    Модель Article представляет статью.
    """
    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
    title = models.CharField(max_length=200, db_index=True)
    content = models.TextField(null=False, blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)


class RSSArticle(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse("blogapp:article", kwargs={"pk": self.pk})