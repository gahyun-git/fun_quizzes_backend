from rest_framework import serializers
from quizzes.models.past_life_quiz import PastLifeQuiz, PastLifeResult
from quizzes.models.category import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PastLifeQuizSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = PastLifeQuiz
        fields = '__all__'

class PastLifeResultSerializer(serializers.ModelSerializer):
    past_life_quiz = PastLifeQuizSerializer(read_only=True)

    class Meta:
        model = PastLifeResult
        fields = '__all__'
