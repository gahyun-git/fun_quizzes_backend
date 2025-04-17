"""
이미지 처리 관련 유틸
"""

import os
import uuid
import textwrap
import logging
from urllib.parse import urljoin
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont 
from django.conf import settings

logger = logging.getLogger(__name__)

def draw_centered_outline_text(
    draw: ImageDraw.Draw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    image_width: int,
    text_color: str = "black",
    outline_color: str = "white",
    outline_width: int = 4
) -> None:
    """
    Parameters:
        draw (ImageDraw.Draw): 텍스트를 그릴 ImageDraw 객체
        text (str): 그릴 텍스트
        y (int): 텍스트의 y 좌표
        font (ImageFont.FreeTypeFont): 사용할 폰트
        image_width (int): 이미지 너비 (중앙 정렬 계산용)
        text_color (str, optional): 텍스트 색상 (기본 "black")
        outline_color (str, optional): 외곽선 색상 (기본 "white")
        outline_width (int, optional): 외곽선 두께 (기본 4)
    """
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (image_width - text_width) / 2  # 중앙 정렬을 위한 x 좌표
    draw.text(
        (x, y),
        text,
        font=font,
        fill=text_color,
        stroke_width=outline_width,
        stroke_fill=outline_color
    )

def add_text_to_image(image_url: str, text_result: dict) -> str:
    """
    이미지에 텍스트 오버레이(이름, 스토리)를 추가한 후, 
    수정된 이미지의 URL을 반환
    
    Parameters:
        image_url (str): 원본 이미지 URL
        text_result (dict): {"name": 전생 이름, "story": 전생 스토리 내용}
        
    Returns:
        str: 텍스트가 추가된 최종 이미지의 URL
    """
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    draw = ImageDraw.Draw(image)
    
    try:
        name_font = ImageFont.truetype(settings.FONT_PATH, 80)
        story_font = ImageFont.truetype(settings.FONT_PATH, 50)
    except IOError as e:
        logger.error("폰트 로드 실패: %s", e)
        name_font = ImageFont.load_default()
        story_font = ImageFont.load_default()

    image_width, image_height = image.size

    name_text = text_result['name']
    draw_centered_outline_text(draw, name_text, 30, name_font, image_width)

    wrapped_story = textwrap.fill(text_result['story'], width=20)
    bbox = draw.textbbox((0, 0), wrapped_story, font=story_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    story_position = ((image_width - text_width) / 2, image_height - text_height - 50)
    draw.text(
        story_position,
        wrapped_story,
        font=story_font,
        fill="black",
        stroke_width=4,
        stroke_fill="white",
        align="center"
    )

    image_file_name = f"{uuid.uuid4().hex}.png"
    output_path = os.path.join(settings.MEDIA_ROOT, image_file_name)
    image.save(output_path)
    final_image_url = urljoin(settings.BASE_URL, f"{settings.MEDIA_URL}{image_file_name}")
    
    return final_image_url