import json
import re
import logging
import openai

logger = logging.getLogger(__name__)

def generate_text_response(prompt: str) -> dict:
    """
    반환값: JSON 파싱된 dict {"name": "전생 이름", "story": "전생 스토리 내용"}
    """
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    content = response.choices[0].message.content

    # Markdown 코드 블록 내의 JSON 부분을 추출하기 위한 정규식
    pattern = r"```(?:json)?\s*(\{.*\})\s*```"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = match.group(1)
    
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        logger.error("JSON 파싱 오류: %s", content)
        result = {"name": "Unknown Soul", "story": content}
    return result

def generate_image_response(prompt: str, size: str = "1024x1024") -> str:
    """
    반환값: 성공 -> 이미지 URL 문자열 반환, 실패 -> None을 반환
    """
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size=size,
        )
        if response.data:
            return response.data[0].url
        else:
            logger.error("이미지 생성 실패: response.data가 비어있습니다.")
            return "생성된 이미지가 없습니다."
    except Exception as e:
        logger.error("이미지 생성 오류: %s", e)
        return None
