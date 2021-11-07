from django.db import models
from django.utils.timezone import now, timedelta


class SingletonModel(models.Model):

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class CreatedUpdatedModel(models.Model):
    """
    A model to reuse the `created_at` and `updated_at` fields
    """
    created_at = models.DateTimeField(default=now, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            self.updated_at = now()
        super().save(*args, **kwargs)


class BotUser(CreatedUpdatedModel):
    # Basic data
    chat_id = models.CharField(max_length=255)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)

    # Permissions
    is_admin = models.BooleanField(default=False)

    # State
    has_blocked_bot = models.BooleanField(default=False)
    last_action_datetime = models.DateTimeField(null=True, blank=True)
    accepted_tos = models.BooleanField(default=False)

    language = models.CharField(max_length=2, choices=(
        ('ES', 'es'),
        ('EN', 'en'),
    ), default=None, null=True, blank=True)

    pocket_request_token = models.CharField(max_length=255, null=True, blank=True)
    pocket_access_token = models.CharField(max_length=255, null=True, blank=True)
    pocket_username = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        name = self.first_name
        if self.last_name is not None:
            name += ' ' + self.last_name
        if self.username is not None:
            name += ' (@{})'.format(self.username)
        return name

    def report_last_action(self):
        self.last_action_datetime = now()


class Broadcast(models.Model):
    success = models.IntegerField(null=True, blank=True)
    errors = models.IntegerField(null=True, blank=True)

    text_es = models.TextField(null=True, blank=True)
    text_en = models.TextField(null=True, blank=True)
    setting_lang = models.CharField(max_length=2, null=True, blank=True)
    sent = models.BooleanField(default=False)


class Feedback(models.Model):
    bot_user = models.ForeignKey(BotUser, on_delete=models.DO_NOTHING)
    message = models.TextField()


class Stats(SingletonModel):
    saved = models.IntegerField(default=0)
