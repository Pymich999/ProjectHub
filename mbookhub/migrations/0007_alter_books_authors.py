# Generated by Django 5.1 on 2024-10-20 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mbookhub', '0006_rename_author_books_authors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='books',
            name='authors',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]