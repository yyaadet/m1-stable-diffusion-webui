# Generated by Django 4.2 on 2023-04-14 07:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stable_diffusion_webui', '0005_promptwordstat_prompt_artistes_prompt_colors_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='promptwordstat',
            unique_together={('word', 'category')},
        ),
    ]
