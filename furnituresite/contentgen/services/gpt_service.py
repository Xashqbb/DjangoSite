from openai import OpenAI
from django.conf import settings

def generate_seo_text(data: dict) -> tuple[str, str]:
    """
    Генерація SEO-тексту через OpenAI або OpenRouter (fallback).
    Повертає (seo_text, source).
    """
    prompt = f"""
    Згенеруй SEO-оптимізований опис для товару e-commerce.

    Назва: {data.get("name")}
    Категорія: {data.get("category")}
    Колір: {data.get("color")}
    Матеріал: {data.get("material")}
    Габарити: {data.get("dimensions")}
    Стиль: {data.get("style")}
    Мітка із зображення: {data.get("image_label")}
    """

    def extract_content(resp):
        if resp.choices and hasattr(resp.choices[0], "message"):
            msg = resp.choices[0].message
            if isinstance(msg, dict):
                return msg.get("content", "").strip()
            return getattr(msg, "content", "").strip()
        return ""

    # 1) OpenAI
    if settings.OPENAI_API_KEY:
        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ти експерт з маркетингу, який пише SEO-описи для товарів."},
                    {"role": "user", "content": prompt}
                ]
            )
            return extract_content(resp), "OpenAI"
        except Exception as e:
            print("⚠️ OpenAI недоступний:", e)

    # 2) OpenRouter
    if settings.OPENROUTER_API_KEY:
        try:
            client = OpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )
            resp = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ти експерт з маркетингу, який пише SEO-описи для товарів."},
                    {"role": "user", "content": prompt}
                ]
            )
            return extract_content(resp), "OpenRouter"
        except Exception as e:
            print("⚠️ OpenRouter теж недоступний:", e)

    # 3) Fallback
    return (
        f"{data.get('name')} — функціональний та надійний виріб для щоденного використання.\n\n"
        "Переваги: зручність у користуванні, продумана конструкція, сучасний дизайн.",
        "Fallback"
    )
