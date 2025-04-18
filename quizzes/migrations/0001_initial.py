# Generated by Django 5.1.7 on 2025-04-11 07:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='카테고리 이름')),
                ('slug', models.SlugField(unique=True, verbose_name='카테고리 슬러그')),
                ('description', models.TextField(blank=True, null=True, verbose_name='카테고리 설명')),
            ],
        ),
        migrations.CreateModel(
            name='PastLifeQuiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='퀴즈 제목')),
                ('description', models.TextField(blank=True, verbose_name='퀴즈 설명')),
                ('require_ad', models.BooleanField(default=True, verbose_name='광고 필요 여부')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='past_life_quizzes', to='quizzes.category', verbose_name='카테고리')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PastLifeResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('birth_date', models.DateField(verbose_name='생년월일')),
                ('birth_time', models.TimeField(blank=True, null=True, verbose_name='태어난 시간')),
                ('past_name', models.CharField(max_length=100, verbose_name='전생이름')),
                ('past_story', models.TextField(verbose_name='전생이야기')),
                ('past_image_url', models.URLField(blank=True, max_length=600, null=True, verbose_name='전생이미지 url')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='결과생성시간')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='사용자(선택)')),
            ],
        ),
    ]
