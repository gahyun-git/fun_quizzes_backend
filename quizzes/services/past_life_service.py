from urllib.parse import urljoin
from django.conf import settings
import logging
from datetime import datetime
from io import BytesIO
import urllib3
from ..utils.image_utils import add_text_to_image
from ..utils.openai_utils import generate_image_response, generate_text_response
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)  # 또는 logger.setLevel(logging.INFO)


def past_life_result(birth_date, birth_time, unknown_birth_time):
    birth_date_str = birth_date.strftime("%Y년 %m월 %d일")
    birth_time_str = "태어난 시간은 모르겠어." if unknown_birth_time or not birth_time else birth_time.strftime("%H시 %M분")

    prompt_for_text = (
        f"생년월일: {birth_date_str}\n"
        f"태어난시간: {birth_time_str}\n"
        "이 정보를 바탕으로 내 전생이 어떤 사람이었는지 상상해줘.\n"
        "신비롭고 재미있는 전생 이야기를 반말로 200자 이내로 작성해줘.\n"
        "반드시 오직 순수 JSON 형식으로 응답해줘. 불필요한 설명이나 마크다운 태그는 제거해줘.\n"
        "예시: {\"name\": \"전생 이름\", \"story\": \"전생 스토리 내용\"}\n"
    )

    text_result = generate_text_response(prompt_for_text)

    prompt_for_image = (
        f"Based on the past life name '{text_result['name']}' and the past life story '{text_result['story']}', "
        "generate an illustration of a single cute anime-style character in Japanese animation or character sticker style. "
        "The character must be large and centered, and should be the ONLY element in the image. "
        "Do NOT include any background elements such as gradients, scenery, objects, icons, UI, props, decorations, shadows, light effects, frames, or text. "
        "The background must be a single solid pastel color. "
        "The style should be soft, colorful, and clean — like a high-quality Japanese character sticker. "
        "Use this image as a reference: https://static.wikia.nocookie.net/demonslayerkorean/images/b/b4/Profile_-_%EC%B9%B4%EB%A7%88%EB%8F%84_%EB%84%A4%EC%A6%88%EC%BD%94.webp/revision/latest?cb=20220618161824&path-prefix=ko"
    )

    # 이미지 생성 시간: ~ 23.768초
    image_url = generate_image_response(prompt_for_image)

    # 이미지 텍스트 추가 시간: ~ 2.937초
    final_image_url = add_text_to_image(image_url, text_result)


    result = {
        "name": text_result['name'],
        "story": text_result['story'],
        "image_url": final_image_url
    }

    return result