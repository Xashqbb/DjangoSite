from django import forms
from furniturestore.models import FurnitureProduct as Product

class UploadForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="Товар",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    image = forms.ImageField(required=False, label="Зображення товару (опціонально)")
    color = forms.CharField(required=False, label="Колір", widget=forms.TextInput(attrs={"class": "form-control"}))
    material = forms.CharField(required=False, label="Матеріал", widget=forms.TextInput(attrs={"class": "form-control"}))
    dimensions = forms.CharField(required=False, label="Габарити (Ш×В×Г)", widget=forms.TextInput(attrs={"class": "form-control"}))
    style = forms.CharField(required=False, label="Стиль (лофт, мінімалізм...)", widget=forms.TextInput(attrs={"class": "form-control"}))

class EditPublishForm(forms.Form):
    seo_text = forms.CharField(widget=forms.Textarea(attrs={"rows": 18, "class": "form-control"}), label="SEO-опис")
    publish = forms.BooleanField(required=False, label="Опублікувати у картці товару (перезапише опис у Product)")
