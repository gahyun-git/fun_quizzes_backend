from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="카테고리 이름")
    slug = models.SlugField(unique=True, verbose_name="카테고리 슬러그")
    description = models.TextField(verbose_name="카테고리 설명", blank=True, null=True)

    def __str__(self):
        return self.name