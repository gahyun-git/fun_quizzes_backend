from django.db import models
from django.conf import settings
from .base_quiz import BaseQuiz
from .category import Category

class PastLifeQuiz(BaseQuiz):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="past_life_quizzes", verbose_name="카테고리")


    def __str__(self):
        return self.title

class PastLifeResult(models.Model):
    ''' 
    user : 로그인한 경우, 비로그인시 null
    birth_date : 생년월일
    birth_time : 시간
    past_name : 전생이름
    past_story : 전생이야기
    past_image_url : 전생이미지
    created_at : 생성시간
    '''
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="사용자(선택)")
    birth_date = models.DateField(verbose_name="생년월일")
    birth_time = models.TimeField(null=True, blank=True, verbose_name="태어난 시간")
    past_name = models.CharField(max_length=100, verbose_name="전생이름")
    past_story = models.TextField(verbose_name="전생이야기")
    past_image_url = models.URLField(max_length=600, verbose_name="전생이미지 url", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="결과생성시간")

    def __str__(self):
        return f"{self.past_name}, {self.past_story}, {self.past_image_url}"
    