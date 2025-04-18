import logging
from ..utils.image_utils import add_text_to_image
from ..utils.openai_utils import generate_image_response, generate_text_response
from jinja2 import Environment, FileSystemLoader


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
    birth_date_str = birth_date.strftime("%Y년 %m월 %d일")
    birth_time_str = (
        "태어난 시간은 몰라." 
        if unknown_birth_time or not birth_time 
        else birth_time.strftime("%H시 %M분"))

    # Jinja2 템플릿으로 텍스트 프롬프트 생성
    prompt_for_text = text_template.render(
        birth_date_str=birth_date_str,
        birth_time_str=birth_time_str
    )

    response = generate_text_response(prompt_for_text)

    # Jinja2 템플릿으로 이미지 프롬프트 생성
    prompt_for_image = image_template.render(
        name=response['name'],
        story=response['story']
    )

    # 이미지 생성 시간: ~ 23.768초
    image_url = generate_image_response(prompt_for_image)

    # 이미지 텍스트 추가 시간: ~ 2.937초
    final_image_url = add_text_to_image(image_url, response)


    result = {
        "name": response['name'],
        "story": response['story'],
        "image_url": final_image_url
    }

    return result