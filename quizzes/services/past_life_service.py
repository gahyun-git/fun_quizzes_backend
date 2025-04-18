import logging
from ..utils.image_utils import add_text_to_image
from ..utils.openai_utils import generate_image_response, generate_text_response
from jinja2 import Environment, FileSystemLoader
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Jinja2 템플릿 환경 설정
template_env = Environment(
    loader=FileSystemLoader("prompts"),
    autoescape=True
)

text_template = template_env.get_template("generate_past_text_prompt.j2")
image_template = template_env.get_template("generate_past_image_prompt.j2")

def past_life_result(birth_date, birth_time, unknown_birth_time):

    logger.info(
        "past_life_result 진입: birth_date=%s, birth_time=%s, unknown=%s",
        birth_date, birth_time, unknown_birth_time
    )

    birth_date_str = birth_date.strftime("%Y년 %m월 %d일")
    birth_time_str = (
        "태어난 시간은 몰라." 
        if unknown_birth_time or not birth_time 
        else birth_time.strftime("%H시 %M분"))

    # 개발 모드(DEBUG=True)에서는 템플릿 파일을 수정하면 서버 재시작 없이도 즉시 반영됨
    # 프로덕션 모드에서는 Jinja2가 템플릿을 캐시하므로, 
    # 프로세스 재시작 혹은 Environment(..., auto_reload=True) 옵션을 켜서 파일 수정 시 자동 갱신

    # Jinja2 템플릿으로 텍스트 프롬프트 생성
    prompt_for_text = text_template.render(
        birth_date_str=birth_date_str,
        birth_time_str=birth_time_str
    )
    logger.debug("생성된 텍스트 프롬프트:\n%s", prompt_for_text)
    response = generate_text_response(prompt_for_text)

    # Jinja2 템플릿으로 이미지 프롬프트 생성
    prompt_for_image = image_template.render(
        name=response['name'],
        story=response['story']
    )

    start = time.time()
    image_url = generate_image_response(prompt_for_image)
    elapsed = time.time() - start
    logger.info("이미지 생성 완료 → URL=%s (%.3f초)", image_url, elapsed)


    start = time.time()
    final_image_url = add_text_to_image(image_url, response)
    elapsed = time.time() - start
    logger.info("최종 이미지 처리 완료 → 최종 URL=%s (%.3f초)", final_image_url, elapsed)


    result = {
        "name": response['name'],
        "story": response['story'],
        "image_url": final_image_url
    }
    logger.debug("past_life_result 결과: %s", result)

    return result