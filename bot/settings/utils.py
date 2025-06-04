from schemas import UserImgGenSettings

async def format_text_for_settings(data: UserImgGenSettings) -> str:
    text = f"Выберите настройку для изменения\n\nТекущие настройки:\n"

    for key, value in data.model_dump().items():
        if key == "lora":
            text += f"\n<b><a href='https://civitai.com/search/models?modelType=LORA'>Lora-модели:</a></b>\n"
            if len(value) < 1:
                text += f"Нет добавленных Lora-моделей\n"
                continue
            for lora in value:
                text += f"<b><a href='{lora['link']}'>{lora['shortname']}</a></b> -> Вес: {lora['weight']}\n"
        elif key == "model":
            text += f"<b><a href='https://civitai.com/models'>Модель:</a></b> <a href='{value['link']}'>{value['shortname']}</a>\n"
        elif key == "scheduler":
            text += f"<b><a href='https://runware.ai/docs/en/image-inference/schedulers'>Синхронизатор:</a></b> {value}\n"
        else:
            text += f"<b>{key}</b>: {str(value)}\n"

    return text

async def validate_link(link: str) -> bool:
    return link.startswith("https://") or link.startswith("http://")