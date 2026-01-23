# Generated manually on 2026-01-23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_recipe_dish_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='cover_url',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='source_url',
        ),
    ]
