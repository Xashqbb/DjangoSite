from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100,null=True)

    def __str__(self):
        return self.name

class FurnitureProduct(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.ImageField(upload_to='main/static/main/img/',null=True,blank=True)
    article = models.CharField(max_length=50)
    model_3d = models.FileField(upload_to='main/static/main/3d_models/', blank=True, null=True)
    color = models.CharField(max_length=50,null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.photo.url
        except:
            url = ''
        return url

def image_folder_path(instance, filename):
    return f'main/static/main/img/img_for_product/{instance.article}/{filename}'

class AdditionalImage(models.Model):
    product = models.ForeignKey(FurnitureProduct, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='additional_images/')

    def __str__(self):
        return f"Additional Image for {self.product.name}"