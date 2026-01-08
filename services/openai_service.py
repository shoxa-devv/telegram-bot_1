from openai import OpenAI

from data.config import OPENAI_API_KEY
from data.history import get_conversation_context


client = OpenAI(api_key=OPENAI_API_KEY)


def chatgpt_text(user_id: int, prompt: str, language: str = "uz") -> str:
    """Generate text reply based on language."""

    language_instruction = ""
    if language == "en":
        language_instruction = (
            "Your primary language is English. However, if the user asks you to translate or speak in another language, you MUST comply and speak that language."
        )
    elif language == "ru":
        language_instruction = (
            "Ваш основной язык — русский. Однако, если пользователь просит перевести или говорить на другом языке, вы ДОЛЖНЫ выполнить просьбу."
        )
    else:
        language_instruction = (
            "Sizning asosiy tilingiz o'zbek tili. Lekin, agar foydalanuvchi boshqa tilga tarjima qilishni yoki boshqa tilda gapirishni so'rasa, siz UNGA AMAL QILISHINGIZ SHART."
        )

    conversation_context = get_conversation_context(user_id)

    if conversation_context:
        full_prompt = f"""Oldingi suhbat tarixi:
{conversation_context}

{language_instruction}

Joriy savol: {prompt}

Javob bering:"""
    else:
        full_prompt = f"""{language_instruction}

Savol: {prompt}

Javob bering:"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": full_prompt}],
    )

    # Record usage
    try:
        if response.usage:
            from data import stats

            stats.record_usage(
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
                model="gpt-4o",
            )
    except Exception as e:
        print(f"Stats error: {e}")

    return response.choices[0].message.content


def speech_to_text(file_path: str) -> str:
    """Convert audio file to text using whisper-1."""
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
    return transcript.text


def text_to_image(text: str, size: str = "1024x1024") -> str:
    response = client.images.generate(
        model="dall-e-3",
        prompt=text,
        n=1,
        size=size,
    )
    return response.data[0].url


def describe_image(image_path: str) -> str:
    """Rasmni tavsiflash uchun OpenAI Vision API"""
    import base64

    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        image_base64 = base64.b64encode(image_data).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Bu rasmni batafsil tavsiflab bering. Rasmda nima bor, ranglar, uslub, mavzu va boshqa muhim detallarni yozing.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            }
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content


def image_to_anime(image_path: str, style: str = "anime") -> str:
    """Rasmni anime yoki multserial uslubida qayta yaratish"""
    description = describe_image(image_path)

    if style == "anime":
        style_prompt = "in anime style, vibrant colors, detailed anime art, Japanese anime character design"
    elif style == "multserial":
        style_prompt = "as cartoon character, colorful cartoon style, animated series character, Disney/Pixar style"
    else:
        style_prompt = "in anime style"

    prompt = (
        f"Create {style_prompt} version of: {description}. Keep the same composition and main elements, but transform the art style."
    )

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024",
    )
    return response.data[0].url


def transform_image_with_instruction(image_path: str, instruction: str) -> str:
    """Apply user instruction to the image by regenerating."""
    description = describe_image(image_path)
    prompt = (
        f"Take the described image and apply the following instruction: {instruction}. "
        f"Keep main subjects and composition. Image description: {description}"
    )
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024",
    )
    return response.data[0].url

