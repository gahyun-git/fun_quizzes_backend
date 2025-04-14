from django.contrib.auth.models import AbstractUser
from django.db import models

# 추후 필요시
class CustomUser(AbstractUser):
    # 유료 구독 여부 및 구독 종료일을 관리
    is_subscribed = models.BooleanField(default=False, verbose_name="구독자 여부")
    subscription_end = models.DateTimeField(null=True, blank=True, verbose_name="구독 종료일")
    
    def __str__(self):
        return self.username