import json
import re
from django.conf import settings
import requests
from PIL import Image, ImageDraw, ImageFont
import openai
import logging
from datetime import datetime
from io import BytesIO
import os

logger = logging.getLogger(__name__)

openai.api_key = settings.OPENAI_API_KEY

def generate_past_life_text_result(birth_date, birth_time, unknown_birth_time):
    birth_date_str = birth_date.strftime("%Y년 %M월 %D일")
    birth_time_str = "태어난 시간은 모르겠어." if unknown_birth_time else birth_time.strftime("%H시 %M분")


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
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("../../fonts/GamjaFlower-Regular.ttf", 40)
    except IOError as e:
        font = ImageFont.load_default()
        logger.error("텍스트 추가 오류: %s", e)
    
    def draw_centered_text(draw, text, y_position, font, image_width):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x_position = (image_width - text_width) / 2
        draw.text((x_position, y_position), text, fill="black", font=font)

    image_width, image_height = image.size

    draw_centered_text(draw, text_result.get("name"), 10, font, image_width)
    draw_centered_text(draw, text_result.get("story"), image_height - 50, font, image_width)

    image_file_name = f"{(text_result.get('name')).strip()}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    output_path = os.path.join(settings.MEDIA_ROOT, image_file_name)
    image.save(output_path)
    image_url = os.path.join(settings.MEDIA_URL, image_file_name)
    return image_url



def past_life_result(birth_date, birth_time, unknown_birth_time):
    text_result = generate_past_life_text_result(birth_date, birth_time, unknown_birth_time)
    prompt_for_image = (
        f"Based on the past life name '{text_result.get('name')}' and the past life story '{text_result.get('story')}', "
        "draw exactly one character in the style of the cute japanese animated.\n"
        "The character must be prominently centered and large in the image.\n"
        "The background must be a plain, uniform color without any additional decorations, doodles, or text.\n"
        "Ensure that only the character is drawn—no extra graphic elements, labels, or text should appear in the image."
    )

    # prompt_for_image = (
    #     f"전생 이름 '{text_result.get('name')}'과 전생 이야기 '{text_result.get('story')}'를 기반으로, "
    #     "미국 애니메이션 the simpsons 스타일의 캐릭터만 딱 하나 그려줘.\n"
    #     "캐릭터는 그림의 중앙에 크게 배치되어야 해. \n"
    #     "배경은 단 하나의 색상으로 깔끔하게 처리해줘. \n"
    #     "The background must be a plain, uniform color without any additional decorations, doodles, or text. \n"
    #     "Ensure that only the character is drawn—no extra graphic elements, labels, or text should appear in the image."
    # )

    # prompt_for_image = (
    # "Reference image style: https://i.pinimg.com/736x/f0/a1/3c/f0a13c737a6b8c1b2e3df0d5a56c57a7.jpg. \n"
    # f"Based on the past life name '{text_result.get('name')}' and the past life story '{text_result.get('story')}', create an illustration that exactly reflects the reference image's style. \n"
    # "The illustration should feature a single character placed exactly in the center of the canvas. \n"
    # "The background must be a plain, uniform color without any additional decorations, doodles, or text. \n"
    # "Ensure that only the character is drawn—no extra graphic elements, labels, or text should appear in the image."
    # )


    # prompt_for_image = (
    #     "https://i.pinimg.com/736x/f0/a1/3c/f0a13c737a6b8c1b2e3df0d5a56c57a7.jpg 이미지의 스타일을 참고해서 \n"
    #     f"전생 이름 '{text_result.get('name')}'과 전생 이야기 '{text_result.get('story')}'를 바탕으로, \n"
    #     "캐릭터를 그려줘. \n"
    #     "아무런 장식, 낙서, 텍스트가 없이 오직 캐릭터 하나만을 중앙에 크게 배치한 그림이어야해. \n"
    #     "배경은 단 한 가지 색상으로 깔끔하게 처리해줘.\n"
    #     # "캐릭터는 카카오톡 이모티콘처럼 단순하고 낙서같은 귀여운 스타일로, 전체적으로 깨끗하고 심플하게 표현해줘."
    # )
    # prompt_for_image = (
    #     f"전생 이름 '{text_result.get('name')}'과 전생 이야기 '{text_result.get('story')}'를 바탕으로, "
    #     "오직 중앙에 크게 낙서한 듯한 하나의 캐릭터만 그려줘. \n"
    #     "배경은 복잡한 장식 없이, 단순한 도트와 기본 도형들로 구성되게 깔끔하게 처리하고, \n"
    #     "텍스트나 불필요한 추가 요소는 전혀 넣지 말아줘. \n"
    #     "캐릭터는 전생의 컨셉을 반영하여 밝고 귀여운 느낌으로 표현해줘."
    # )


    # prompt_for_image = (
    #     f"전생 이름 '{text_result.get('name')}'과 전생 이야기 '{text_result.get('story')}'를 바탕으로, "
    #     "오직 중앙에 크게 하나의 캐릭터만 배치한 그림을 그려줘. "
    #     "배경은 복잡한 장식 없이, 단순한 도트와 기본 도형들만 사용하여 깔끔하게 처리해줘. "
    #     "텍스트나 추가적인 요소는 전혀 포함하지 말고, 파스텔톤 색상으로 따뜻하고 귀여운 느낌을 줘."
    # )

    # prompt_for_image = (
    #     f"전생 이름 '{text_result.get('name')}'과 전생 이야기 '{text_result.get('story')}'를 바탕으로, "
    #     "손으로 낙서한 듯한 알록달록하고 귀엽고 재미있는 분위기의 캐릭터 일러스트를 그려줘. "
    #     "전체 그림은 다채로운 파스텔 색상을 사용하고, 자유로운 낙서 느낌의 장식(만화적인 선, 도트, 단순 도형 등)이 어우러지도록 해줘. "
    #     "캐릭터는 중앙에 배치하며, 배경은 밝고 생동감 있게 처리해, 전체적으로 손으로 대충 그린 듯한 느낌을 주고 텍스트는 들어가지 않게 만들어줘."
    # )

    # prompt_for_image = (
    #     f"전생이야기: {text_result.get('story')}\n\n"
    #     "위 전생 이야기를 바탕으로 한국 귀여운 낙서 스타일 그림. 카카오톡 이모티콘 느낌의 단순하고 귀여운 캐릭터가 등장해.\n"
    #     f"이미지 상단 중앙에 '{text_result.get('name')}'이라는 한국어 이름을 크고 굵은 글씨로 넣어줘.\n"
    #     "이미지 하단 중앙에는 다음 한국어로 전생 이야기를 줄바꿈해서 가독성 좋게 넣어줘.\n"
    #     "전체 그림은 비비드한 색상, 굵은 검정 선으로 구성하고, "
    #     "글자와 캐릭터는 충분한 여백을 줘서 텍스트가 절대 잘리지 않게 해줘."
    # )

    # prompt_for_image = (
    #     f"전생이야기: {text_result.get('story')}\n\n"
    #     f"위 전생 이야기를 바탕으로 한국 귀여운 낙서 스타일 그림. 카카오톡 이모티콘 느낌의 단순하고 귀여운 캐릭터가 등장해.\n "
    #     f"이미지 상단 중앙에 '{text_result.get('name')}'이라는 한국어 이름을 크고 굵은 글씨로 넣어줘.\n"
    #     f"이미지 하단 중앙에는 다음 한국어로 전생 이야기를 줄바꿈해서 가독성 좋게 넣어줘\n"
    #     f"전체 그림은 비비드한 색상, 굵은 검정 선으로 구성하고 "
    #     f"글자와 캐릭터는 충분한 여백을 줘서 텍스트가 절대 잘리지 않게 해줘."
    # )

    # prompt_for_image = (
    #     f"전생이야기: {text_result.get('story')}\n\n"
    #     "위 전생 이야기를 바탕으로, 한국의 특색 있는 귀여운 낙서 스타일의 그림을 그려줘. "
    #     "그림은 전체적으로 자유로운 낙서 느낌을 가지면서도, 카카오톡 이모티콘 같은 따뜻하고 사랑스러운 분위기를 표현해야 해. "
    #     "특히, 그림 안의 한글 텍스트는 완벽한 형태보다는 낙서체 특유의 자유롭고 약간은 거칠지만 독창적인 느낌으로 나타나야 해. "
    #     f"예를 들어, 이미지 상단 중앙에 '{text_result.get('name')}'라는 글자가 자연스럽게 낙서된 것처럼 배치되고, "
    #     "나머지 이미지는 전생 이야기가 반영된 감성적인 캐릭터와 배경으로 구성되어 있으면 좋겠어. "
    #     "전체적인 분위기는 파스텔 색조를 사용해서 부드럽고 아기자기하게 표현되어야 해."
    # )

    # prompt_for_image = (
    #     f"전생이야기: {text_result.get('story')}\n\n"
    #     "이 전생 이야기를 바탕으로, 한국의 귀여운 낙서 스타일 일러스트를 그려줘. "
    #     "그림은 카카오톡 이모티콘 같은 따뜻하고 자유로운 느낌의 손으로 그린 듯한 낙서체로 표현되어야 해. "
    #     f"이미지 상단 중앙에는 '{text_result.get('name')}'라는 텍스트가, 명확한 인쇄체가 아니라 오히려 독창적인 손글씨 낙서 스타일로 자연스럽게 나타나도록 해. "
    #     "전체적으로 파스텔 톤의 부드러운 색감을 사용하고, 텍스트나 캐릭터가 너무 깔끔하지 않고 약간 불규칙하며, 자유로운 낙서의 느낌을 살려줘. "
    #     "글자가 완벽히 읽히지 않아도 괜찮으니, 오히려 낙서체의 매력이 드러나도록 표현해줘."
    # )

    image_url = add_text_to_image(generate_past_life_image_result(prompt_for_image), text_result)

    result = {
        "name": text_result.get("name"),
        "story": text_result.get("story"),
        "image_url": f"http://localhost:8000{image_url}"
    }
    print(result["image_url"])
    print(result.get("image_url"))

    return result