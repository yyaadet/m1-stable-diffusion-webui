# Generated by Django 4.2 on 2023-04-14 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stable_diffusion_webui', '0007_promptwordstat_ratio'),
    ]

    operations = [
        migrations.AddField(
            model_name='prompt',
            name='exclude',
            field=models.TextField(blank=True, null=True),
        ),
    ]
