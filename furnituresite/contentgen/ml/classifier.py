import warnings

try:
    import torch
    from PIL import Image
    from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
except Exception as e:
    torch = None
    Image = None
    EfficientNet_B0_Weights = None
    efficientnet_b0 = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

_device = None
_model = None
_preprocess = None
_categories = None

def _init_device():
    global _device
    if _device is not None:
        return _device
    if torch is None:
        _device = "cpu"
    else:
        _device = "cuda" if torch.cuda.is_available() else "cpu"
    return _device

def _load_model_once():
    """
    Завантаження попередньо натренованої EfficientNet-B0 з ImageNet-вагами
    Якщо torch/torchvision недоступні — кинемо кероване виключення
    """
    global _model, _preprocess, _categories
    if _model is not None and _preprocess is not None:
        return _model, _preprocess, _categories

    if _IMPORT_ERROR is not None:
        raise RuntimeError(f"torch/torchvision недоступні: {_IMPORT_ERROR}")

    device = _init_device()
    weights = EfficientNet_B0_Weights.DEFAULT
    _model = efficientnet_b0(weights=weights)
    _model.eval().to(device)
    _preprocess = weights.transforms()
    _categories = weights.meta.get("categories", [])
    return _model, _preprocess, _categories

def classify_image_pil(pil_img: "Image.Image") -> dict:
    """
    Повертає top-1 категорію ImageNet
    Відповідь: {"label": <str>, "prob": <float>}
    """
    if pil_img is None:
        raise ValueError("Зображення відсутнє.")
    model, preprocess, categories = _load_model_once()

    img = pil_img.convert("RGB")
    batch = preprocess(img).unsqueeze(0)
    device = _init_device()
    if device == "cuda":
        batch = batch.to("cuda")

    with torch.no_grad():
        logits = model(batch)
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]

    top_idx = int(probs.argmax())
    top_prob = float(probs[top_idx])
    top_label = categories[top_idx] if categories else str(top_idx)
    return {"label": top_label, "prob": round(top_prob, 4)}

def rough_map_to_furniture(label: str) -> str:
    """
    Грубе правила-меппінг з ImageNet -> наші меблеві категорії.
    Якщо не впевнені — повертаємо оригінальну англ. мітку.
    """
    if not label:
        return ""
    l = label.lower()

    # столи / парти / тумби-письмові
    if any(k in l for k in ["desk", "table", "workbench"]):
        return "стіл"

    # шафи / комоди / гардероби / шафи-купе
    if any(k in l for k in ["wardrobe", "closet", "cabinet", "cupboard", "chest"]):
        return "шафа"

    # полиці / книжкові шафи
    if any(k in l for k in ["shelf", "bookcase", "etagere"]):
        return "стелаж"

    # тумби / приліжкові
    if any(k in l for k in ["nightstand", "dresser", "drawer", "sideboard"]):
        return "тумба"

    return label

def safe_classify(pil_img: "Image.Image") -> dict:
    """
    «Безпечний» виклик для в’юхи: якщо torch відсутній або сталася помилка,
    повертає {"label": "", "prob": 0.0} без падіння всього запиту
    """
    try:
        return classify_image_pil(pil_img)
    except Exception as e:
        warnings.warn(f"classify error: {e}")
        return {"label": "", "prob": 0.0}
