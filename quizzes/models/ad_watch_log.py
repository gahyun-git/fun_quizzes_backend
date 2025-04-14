from django.db import models
from django.conf import settings
from .past_life_quiz import PastLifeResult

class AdWatchLog(models.Model):
    result = models.ForeignKey(PastLifeResult, on_delete=models.CASCADE, related_name='ad_watch_logs', verbose_name="광고시청완료 결과")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="사용자(선택)")
    watched_at = models.DateTimeField(auto_now_add=True, verbose_name="광고시청 완료시간")

    def __str__(self):
        return f"AdWatch for {self.result} at {self.watched_at}"