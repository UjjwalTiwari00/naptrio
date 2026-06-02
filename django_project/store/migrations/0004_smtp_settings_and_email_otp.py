import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_sitesettings'),
    ]

    operations = [
        # Add SMTP fields to SiteSettings
        migrations.AddField(
            model_name='sitesettings',
            name='smtp_host',
            field=models.CharField(
                default='smtp.gmail.com',
                help_text='SMTP server hostname, e.g. smtp.gmail.com',
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='smtp_port',
            field=models.PositiveIntegerField(
                default=587,
                help_text='SMTP port (587 for TLS, 465 for SSL, 25 for plain)',
            ),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='smtp_use_tls',
            field=models.BooleanField(
                default=True,
                help_text='Use STARTTLS (port 587). Disable for SSL (port 465).',
            ),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='smtp_use_ssl',
            field=models.BooleanField(
                default=False,
                help_text='Use SSL (port 465). Mutually exclusive with TLS.',
            ),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='smtp_user',
            field=models.CharField(
                blank=True,
                help_text='Email address used to authenticate with the SMTP server.',
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='smtp_password',
            field=models.CharField(
                blank=True,
                help_text='App password / SMTP password. For Gmail use an App Password.',
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='from_email',
            field=models.EmailField(
                blank=True,
                help_text="'From' address shown to recipients. Defaults to smtp_user if blank.",
            ),
        ),
        # Create EmailOTP model
        migrations.CreateModel(
            name='EmailOTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField()),
                ('otp', models.CharField(max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('is_used', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
