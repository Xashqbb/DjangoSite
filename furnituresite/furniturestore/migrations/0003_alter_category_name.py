# Generated by Django 4.2.4 on 2023-08-21 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('furniturestore', '0002_alter_category_name_alter_furnitureproduct_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100, null=True),
        ),
    ]