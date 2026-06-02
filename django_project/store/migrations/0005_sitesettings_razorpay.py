from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_smtp_settings_and_email_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='razorpay_key_id',
            field=models.CharField(
                blank=True,
                help_text='Razorpay Key ID — starts with rzp_test_ or rzp_live_',
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='razorpay_key_secret',
            field=models.CharField(
                blank=True,
                help_text='Razorpay Key Secret. Keep this confidential.',
                max_length=255,
            ),
        ),
    ]
