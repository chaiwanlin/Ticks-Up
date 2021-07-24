# Generated by Django 3.2.3 on 2021-07-23 18:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0005_alter_stockposition_ticker'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockposition',
            name='ticker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assets.ticker'),
        ),
        migrations.RemoveField(
            model_name='ticker',
            name='portfolio',
        ),
        migrations.AddField(
            model_name='ticker',
            name='portfolio',
            field=models.ManyToManyField(to='assets.Portfolio'),
        ),
    ]
