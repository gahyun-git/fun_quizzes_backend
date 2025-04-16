import json
import re
from django.conf import settings
import requests
from PIL import Image, ImageDraw, ImageFont, ImageStat
import openai
import logging
from datetime import datetime
import uuid
from io import BytesIO
import os
import textwrap
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logger = logging.getLogger(__name__)

openai.api_key = settings.OPENAI_API_KEY

def generate_past_life_text_result(birth_date, birth_time, unknown_birth_time):
    birth_date_str = birth_date.strftime("%Y년 %m월 %d일")
    birth_time_str = "태어난 시간은 모르겠어." if unknown_birth_time or not birth_time else birth_time.strftime("%H시 %M분")


    prompt = (
        f"생년월일: {birth_date_str}"
        f"태어난시간: {birth_time}"
        "이 정보를 바탕으로 내 전생이 어떤 사람이었는지 상상해줘.\n"
        "신비롭고 재미있는 전생 이야기를 반말로 200자 이내로 작성해줘.\n"
        "반드시 아래 형식의 JSON으로 응답해줘:\n"
        "{\n  \"name\": \"전생 이름\",\n  \"story\": \"전생 스토리 내용\"\n}"
    )

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content
    try:
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
        else:
            raise ValueError("JSON 파싱실패.")
    except Exception:
        result = {"name": "Unknown Soul", "story": content}

    return result


def generate_past_life_image_result(prompt_for_image):
    # size
    # dall-e-2: 256x256, 512x512, 1024x1024
    # dall-e-3: 1024x1024, 1792x1024, 1024x1792
    try:    
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt_for_image,
            n=1,
            size="1024x1024",
        )
        logger.info("이미지 생성 응답: %s", response)

        result = response.data[0].url if response.data else "생성된 이미지가 없습니다."
    except Exception as e:
        logger.error("이미지 생성 오류: %s", e)
        result = None
    
    return result

def add_text_to_image(image_url, text_result):
    # 이미지 가져오기 (타임아웃 10초 설정)
    response = requests.get(image_url, timeout=10)
    image = Image.open(BytesIO(response.content)).convert("RGBA")
    draw = ImageDraw.Draw(image)

    # 폰트 로드 (설정된 폰트 사용, 실패하면 기본 폰트)
    try:
        name_font = ImageFont.truetype(settings.FONT_PATH, 80)
    except IOError:
        name_font = ImageFont.load_default()
    try:
        story_font = ImageFont.truetype(settings.FONT_PATH, 50)
    except IOError:
        story_font = ImageFont.load_default()

    image_width, image_height = image.size

    def draw_outline_text(draw, text, position, font, text_color, outline_color, outline_width=3):
        x, y = position
        # 여러 방향으로 텍스트를 그려 외곽선을 만듦
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        draw.text((x, y), text, font=font, fill=text_color)

    # 이름 처리
    const_name = text_result.get("name", "")
    name_bbox = draw.textbbox((0, 0), const_name, font=name_font)
    name_width = name_bbox[2] - name_bbox[0]
    name_x = (image_width - name_width) / 2
    name_y = 30  # 상단 고정 위치

    draw_outline_text(draw, const_name, (name_x, name_y), name_font, text_color="black", outline_color="white", outline_width=4)

    # 스토리 처리 (자동 줄바꿈 width=25는 필요에 따라 조절)
    const_story = text_result.get("story", "")
    wrapped_story = textwrap.fill(const_story, width=25)
    story_bbox = draw.textbbox((0, 0), wrapped_story, font=story_font)
    story_width = story_bbox[2] - story_bbox[0]
    story_x = (image_width - story_width) / 2
    story_y = image_height - story_bbox[3] - 50

    draw_outline_text(draw, wrapped_story, (story_x, story_y), story_font, text_color="black", outline_color="white", outline_width=3)

    # 이미지 저장
    image_file_name = f"{uuid.uuid4().hex}.png"
    output_path = os.path.join(settings.MEDIA_ROOT, image_file_name)
    image.save(output_path)

    final_image_url = f"{settings.BASE_URL}{settings.MEDIA_URL}{image_file_name}"
    return final_image_url



def past_life_result(birth_date, birth_time, unknown_birth_time):
    text_result = generate_past_life_text_result(birth_date, birth_time, unknown_birth_time)
    prompt_for_image = (
        f"Based on the past life name '{text_result.get('name')}' and the past life story '{text_result.get('story')}', "
        "generate an illustration of a single cute anime-style character in Japanese animation or character sticker style. "
        "The character must be large and centered, and should be the ONLY element in the image. "
        "Do NOT include any background elements such as gradients, scenery, objects, icons, UI, props, decorations, shadows, light effects, frames, or text. "
        "The background must be a single solid pastel color. "
        "The style should be soft, colorful, and clean — like a high-quality Japanese character sticker. "
        "Use this image as a reference: https://static.wikia.nocookie.net/demonslayerkorean/images/b/b4/Profile_-_%EC%B9%B4%EB%A7%88%EB%8F%84_%EB%84%A4%EC%A6%88%EC%BD%94.webp/revision/latest?cb=20220618161824&path-prefix=ko"
    )


    image_url = add_text_to_image(generate_past_life_image_result(prompt_for_image), text_result)

    result = {
        "name": text_result.get("name"),
        "story": text_result.get("story"),
        "image_url": image_url
    }

    return result