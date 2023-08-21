from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100)

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
