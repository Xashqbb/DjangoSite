from openai import OpenAI
from django.conf import settings


def generate_seo_text(data: dict) -> tuple[str, str]:
    """
    Генерація SEO-тексту відповідно до методики (Розділ 2.3).
    Якщо атрибути відсутні, вони замінюються на загальні позитивні характеристики,
    щоб уникнути фраз "не вказано".
    """

    # 1. Допоміжна функція для очищення даних
    def clean(val):
        if val and isinstance(val, str) and val.strip().lower() not in ["", "не вказано", "none", "null"]:
            return val.strip()
        return None

    # Отримуємо чисті вхідні дані
    name = data.get("name", "Товар")
    category = data.get("category", "Меблі")

    raw_style = clean(data.get("style"))
    raw_material = clean(data.get("material"))
    raw_color = clean(data.get("color"))
    raw_dimensions = clean(data.get("dimensions"))
    image_label = clean(data.get("image_label"))

    # 2. ЛОГІКА ЗАМІНИ ПУСТОТИ НА ЗАГАЛЬНІ СЛОВА
    # Якщо даних немає, підставляємо "заглушку", яка звучить як перевага.
    # Це змушує AI писати гарно, не вигадуючи цифри/факти.

    p_style = raw_style if raw_style else "сучасний дизайн, що легко інтегрується в інтер'єр"
    p_material = raw_material if raw_material else "якісні матеріали, що забезпечують надійність та довговічність"
    p_dimensions = raw_dimensions if raw_dimensions else "ергономічні габарити для зручного розміщення"
    p_color = raw_color if raw_color else "гармонійне кольорове рішення"

    # Формування особливостей (додаємо detected label як особливість, якщо є)
    features = "функціональність та естетичність"
    if image_label:
        features += f", візуально нагадує {image_label}"

    # 3. Формування SEO-фраз (тільки з того, що реально є)
    keywords_list = [category, f"«{category} {name}»"]
    if raw_style: keywords_list.append(f"«{category} {raw_style}»")
    if raw_color: keywords_list.append(f"«{category} {raw_color}»")
    # Якщо атрибутів мало, додаємо загальні
    if len(keywords_list) < 3:
        keywords_list.append(f"«купити {category}»")

    keywords_str = ", ".join(keywords_list)

    # 4. СТРУКТУРА ПРОМТА (згідно з методикою 2.3)
    # Розділяємо на "Інформація" та "Вимоги"

    prompt = f"""
Створи унікальний та SEO–оптимізований опис для товару e–commerce у категорії меблів.
Працюй з інформацією нижче.

БЛОК ХАРАКТЕРИСТИК ТОВАРУ:
Назва: {name}
Категорія: {category}
Матеріали: {p_material}
Габарити: {p_dimensions}
Колір: {p_color}
Стиль: {p_style}
Призначення: вітальня, спальня, офіс (універсальне)
Додаткові особливості: {features}

ІНСТРУКЦІЇ ДО ГЕНЕРАЦІЇ (Вимоги до тексту):
1. Створити унікальний опис українською мовою (2–3 абзаци зв'язного тексту).
2. Забезпечити логічну структуру:
   - Вступ: передає ідею виробу та його призначення.
   - Основна частина: описує характеристики (використовуй дані з блоку вище) в художньому стилі.
   - Висновок: переваги використання у домі або офісі.
3. Використовувати природні SEO–фрази: {keywords_str}.
4. Уникнення вигадок:
   - Якщо у полі "Матеріали" чи "Габарити" написано загальну фразу (наприклад, "якісні матеріали"), НЕ вигадуй конкретний тип (не пиши "дуб", "сосна", "150 см"), а описуй саме надійність та якість.
5. Не дублювати характеристики списком – подати їх у вигляді плавного тексту.
6. Уникати кліше ("ідеальний вибір", "найкращий у світі") та тавтологій.
7. Тон: професійний, доброзичливий, комерційний, але коректний.

Важливо: Текст має виглядати завершеним і продаючим, навіть якщо конкретних цифр немає. Роби акцент на затишку, порядку та стилі.
    """

    def extract_content(resp):
        if resp.choices and hasattr(resp.choices[0], "message"):
            msg = resp.choices[0].message
            if isinstance(msg, dict):
                return msg.get("content", "").strip()
            return getattr(msg, "content", "").strip()
        return ""

    # 2) OpenRouter
    if getattr(settings, "OPENROUTER_API_KEY", None):
        try:
            client = OpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )
            resp = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ти професійний копірайтер меблевого магазину. Ти вмієш гарно описувати загальні переваги товару, якщо точні технічні дані відсутні."},
                    {"role": "user", "content": prompt}
                ]
            )
            return extract_content(resp), "OpenRouter"
        except Exception as e:
            print("⚠️ OpenRouter error:", e)

    # 3) Fallback (Заглушка)
    fallback_text = (
        f"{name} — це стильне та практичне рішення для вашого інтер'єру в категорії «{category}». "
        f"Виріб має {p_style}, що дозволяє гармонійно вписати його в дизайн приміщення.\n\n"
        f"Завдяки використанню {p_material}, меблі відзначаються довговічністю. "
        f"{p_dimensions.capitalize()} роблять цю модель зручною для будь-якого простору.\n\n"
        "Обираючи цей товар, ви отримуєте поєднання естетики та функціональності. "
        "Замовляйте зараз, щоб оновити свій простір."
    )

    return fallback_text, "Fallback"