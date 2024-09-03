from django.db import models


class TelegramIDMIxin(models.Model):
    tg_id = models.IntegerField(
        verbose_name='Unique Telegram ID',
        unique=True,
        null=True,
        blank=True,
        help_text=('If this field does not specified,'
                   'user wont be able to login via telegram')
    )

    class Meta:
        abstract = True
