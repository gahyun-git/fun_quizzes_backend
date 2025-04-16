from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import logging
from datetime import datetime

from quizzes.models.past_life_quiz import PastLifeQuiz, PastLifeResult
from quizzes.serializers.past_life import PastLifeQuizSerializer, PastLifeResultSerializer
from quizzes.services.past_life_service import past_life_result

logger = logging.getLogger(__name__)

class PastLifeQuizViewSet(viewsets.ModelViewSet):
    queryset = PastLifeQuiz.objects.all()
    serializer_class = PastLifeQuizSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PastLifeResultViewSet(viewsets.ModelViewSet):
    queryset = PastLifeResult.objects.all()
    serializer_class = PastLifeResultSerializer

    def retrieve(self, request, pk=None):
        try:
            result = PastLifeResult.objects.get(pk=pk)
            serializer = self.get_serializer(result)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PastLifeResult.DoesNotExist:
            return Response({"error": "결과를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        birth_date_str = request.data.get('birth_date')
        birth_time_str = request.data.get('birth_time')
        ampm = request.data.get('ampm', '오전')
        unknown_birth_time = request.data.get('unknown_birth_time', False)
        
        if isinstance(unknown_birth_time, str):
            unknown_birth_time = unknown_birth_time.lower() in ['true', '1']
        
        if not birth_date_str:
            logger.error("생년월일 누락: 요청 데이터에 'birth_date'가 없습니다.")
            return Response({"error": "생년월일이 필수입니다."}, status=status.HTTP_400_BAD_REQUEST)

        if not birth_time_str and not unknown_birth_time:
            logger.error("태어난 시간 누락: 'birth_time'이 없으며, 체크박스도 선택되지 않음.")
            return Response({"error": "태어난 시간이 없으면 체크박스를 선택해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            logger.info(f"Parsed birth_date: {birth_date}")

            if birth_time_str and not unknown_birth_time:
                birth_time = datetime.strptime(birth_time_str, "%H:%M").time()
                if ampm == '오후':
                    birth_time = birth_time.replace(hour=birth_time.hour + 12)
                logger.info(f"Parsed birth_time: {birth_time}")
            else:
                birth_time = None

            result = past_life_result(birth_date, birth_time, unknown_birth_time)
        except ValueError as e:
            logger.error(f"Date parsing error: {e}")
            return Response(
                {"error": f"날짜 형식 오류: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"전생 결과 생성 실패: {e}")
            return Response(
                {"error": f"전생 결과 생성 실패: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = self.get_serializer(data={
            "birth_date": birth_date,
            "birth_time": birth_time,
            "past_name": result.get("name", "Unknown"),
            "past_story": result.get("story", "No story available"),
            "past_image_url": result.get("image_url", "No image available"),
            "user": request.user if request.user.is_authenticated else None,
            "created_at": datetime.now(),
        })
        
        if not serializer.is_valid():
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        headers = self.get_success_headers(serializer.data)
        logger.info("전생 결과 저장: 사용자 %s", request.user)

        return Response(serializer.data, status.HTTP_201_CREATED, headers=headers)

