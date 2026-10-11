from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from core import settings


# Create your models here.

class User(AbstractUser):
    phone_number = models.CharField(max_length=11, blank=True)
    is_seller = models.BooleanField(default=False)
    def __str__(self):
        return self.username


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    reverse_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=11, blank=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    full_address = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-is_default', '-id']
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'{self.title}-{self.user.username}'

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk and not Address.objects.filter(user=self.user).exists():
                self.is_default = True
            if self.is_default:
                (Address.objects.filter(user=self.user,is_default=True).exclude(
                    pk=self.pk)).update(is_default=False)
            super().save(*args, **kwargs)


