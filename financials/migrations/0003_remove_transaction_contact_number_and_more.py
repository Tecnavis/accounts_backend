# Generated by Django 5.1.5 on 2025-02-28 08:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financials', '0002_transaction_discount_amount'),
        ('partner', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='contact_number',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='email',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='username',
        ),
        migrations.AddField(
            model_name='transaction',
            name='partner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='partner.partnerprofile'),
        ),
    ]
