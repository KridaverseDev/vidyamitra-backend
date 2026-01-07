# Generated manually for UserAPIKey model
# Run: python manage.py migrate to apply

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAPIKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(choices=[('openai', 'OpenAI'), ('gemini', 'Google Gemini'), ('grok', 'Grok (xAI)')], help_text='API provider (OpenAI, Gemini, Grok)', max_length=20)),
                ('encrypted_key', models.TextField(help_text='Encrypted API key stored securely')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this API key is currently active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(help_text='User who owns this API key', on_delete=django.db.models.deletion.CASCADE, related_name='api_keys', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User API Key',
                'verbose_name_plural': 'User API Keys',
            },
        ),
        migrations.AddIndex(
            model_name='userapikey',
            index=models.Index(fields=['user', 'provider'], name='user_userap_user_id_idx'),
        ),
        migrations.AddIndex(
            model_name='userapikey',
            index=models.Index(fields=['user', 'is_active'], name='user_userap_user_id_is_active_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='userapikey',
            unique_together={('user', 'provider')},
        ),
    ]

