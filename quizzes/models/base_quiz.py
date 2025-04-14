from django.db import models

class BaseQuiz(models.Model):
    title = models.CharField(max_length=200, verbose_name="퀴즈 제목")
    description = models.TextField(verbose_name="퀴즈 설명", blank=True)
    require_ad = models.BooleanField(default=True, verbose_name="광고 필요 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    
    class Meta:
        abstract = True    
