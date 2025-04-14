from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.past_life_viewsets import PastLifeQuizViewSet, PastLifeResultViewSet

router = DefaultRouter()
router.register(r'past-life-quizzes', PastLifeQuizViewSet, basename='past-life-quizzes')
router.register(r'past-life-results', PastLifeResultViewSet, basename='past-life-results')

urlpatterns = [
    path('', include(router.urls)),  # ViewSet의 URL 포함
]