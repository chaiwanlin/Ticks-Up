# Generated by Django 3.2.3 on 2021-07-28 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0004_alter_ticker_portfolio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticker',
            name='portfolio',
            field=models.ManyToManyField(to='assets.Portfolio'),
        ),
    ]