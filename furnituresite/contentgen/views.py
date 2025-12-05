from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from PIL import Image

from furniturestore.models import FurnitureProduct as Product
from .forms import UploadForm, EditPublishForm
from .models import GeneratedDescription
from .ml.classifier import safe_classify, rough_map_to_furniture
from .services.gpt_service import generate_seo_text


def staff_required(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(staff_required)
def upload_view(request):
    """
    Приймає дані, обробляє зображення (завантажене або з БД),
    класифікує та генерує опис через GPT.
    """
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.cleaned_data["product"]
            use_existing = form.cleaned_data.get("use_product_image")
            image_file = None

            if use_existing:
                if hasattr(product, 'photo') and product.photo:
                    image_file = product.photo
                #Якщо 'photo' немає, спробуємо стандартне 'image'
                elif hasattr(product, 'image') and product.image:
                    image_file = product.image
                else:
                    messages.warning(request,
                                     "У обраного товару немає фото в базі (перевірено поля 'photo' та 'image').")

            if not image_file:
                image_file = form.cleaned_data.get("image")  # Це UploadedFile

            # Очищення атрибутів
            color = (form.cleaned_data.get("color") or "").strip()
            material = (form.cleaned_data.get("material") or "").strip()
            dimensions = (form.cleaned_data.get("dimensions") or "").strip()
            style = (form.cleaned_data.get("style") or "").strip()

            # 1) Класифікація
            detected_label = ""
            mapped_category = ""
            if image_file:
                try:
                    # Якщо файл з БД, його треба відкрити
                    if hasattr(image_file, 'open'):
                        image_file.open('rb')

                    pil = Image.open(image_file)
                    res = safe_classify(pil)
                    detected_label = res.get("label", "")
                    mapped_category = rough_map_to_furniture(detected_label)

                    # Повертаємо курсор на початок для збереження
                    image_file.seek(0)
                except Exception as e:
                    messages.warning(request, f"Класифікація пропущена: {e}")

            # Визначення категорії для промта
            category_for_prompt = ""
            if hasattr(product, "category") and getattr(product, "category", None):
                category_for_prompt = getattr(product.category, "name", "") or ""

            if not category_for_prompt:
                category_for_prompt = mapped_category or "Меблі"

            # 2) Створення запису GeneratedDescription
            gen = GeneratedDescription.objects.create(
                product=product,
                image=image_file if image_file else None,
                detected_category=mapped_category or detected_label,
                features_json={
                    "color": color,
                    "material": material,
                    "dimensions": dimensions,
                    "style": style,
                    "source_category": category_for_prompt
                },
                status="draft",
                created_by=request.user,
            )

            # 3) Генерація GPT
            try:
                data = {
                    "name": product.name,
                    "category": category_for_prompt,
                    "color": color,
                    "material": material,
                    "dimensions": dimensions,
                    "style": style,
                    "image_label": mapped_category if mapped_category else detected_label,
                }

                seo_text, source = generate_seo_text(data)

                gen.seo_text = seo_text
                gen.source = source
                gen.save()

                if source in ["OpenAI", "OpenRouter"]:
                    messages.success(request, f"Опис успішно згенеровано ({source}).")
                else:
                    messages.warning(request, "AI недоступний. Використано шаблонний опис.")

            except Exception as e:
                gen.seo_text = "Сталася помилка генерації. Спробуйте пізніше."
                gen.status = "failed"
                gen.save()
                messages.error(request, f"Критична помилка: {e}")

            return redirect(reverse("contentgen:editor", kwargs={"pk": gen.pk}))
    else:
        form = UploadForm()
    return render(request, "contentgen/upload.html", {"form": form})


@login_required
@user_passes_test(staff_required)
def editor_view(request, pk: int):
    gen = get_object_or_404(GeneratedDescription, pk=pk)
    if request.method == "POST":
        form = EditPublishForm(request.POST)
        if form.is_valid():
            seo_text = form.cleaned_data["seo_text"]
            publish = form.cleaned_data["publish"]

            gen.seo_text = seo_text
            gen.status = "draft"
            gen.save()

            if publish:
                product = gen.product
                if hasattr(product, "description"):
                    product.description = seo_text
                    product.save()
                    gen.status = "published"
                    gen.save()
                    messages.success(request, "Опис опубліковано в картці товару.")
                else:
                    messages.warning(request, "У моделі товару відсутнє поле description.")
            else:
                messages.info(request, "Зміни збережено (чернетка).")

            return redirect(reverse("contentgen:editor", kwargs={"pk": gen.pk}))
    else:
        form = EditPublishForm(initial={"seo_text": gen.seo_text})

    return render(request, "contentgen/editor.html", {"gen": gen, "form": form})


@login_required
@user_passes_test(staff_required)
def list_view(request):
    # 1. Отримуємо всі записи, як і раніше
    items_list = GeneratedDescription.objects.select_related('product').order_by('-created_at')
    # 2. Отримуємо кількість записів на сторінку з GET-запиту (за замовчуванням 10)
    per_page = request.GET.get('per_page', 10)
    # Перевірка на валідність числа (щоб не зламалось, якщо передадуть текст)
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 50]:  # Дозволяємо тільки ці значення
            per_page = 10
    except (ValueError, TypeError):
        per_page = 10
    # 3. Створюємо пагінатор
    paginator = Paginator(items_list, per_page)
    # 4. Отримуємо номер поточної сторінки
    page_number = request.GET.get('page')
    # get_page автоматично обробляє помилки (якщо сторінка не число або більше максимуму)
    page_obj = paginator.get_page(page_number)
    # 5. Передаємо context у шаблон
    return render(request, "contentgen/list.html", {
        "page_obj": page_obj,  # <--- Шаблон чекає саме цю змінну!
        "per_page": per_page  # Щоб зберегти вибір у випадаючому списку
    })