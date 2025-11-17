from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
class User(AbstractUser):
    pass

class JobListing(models.Model):
    my_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField()
    timestamp = models.DateTimeField(auto_now_add=True)
    signed_up = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    percentage = models.DecimalField(
        max_digits=3,  # Allows for values like 100
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        default=0
        )

    @property
    def deadline_passed(self):
        return timezone.now() > self.deadline

    @property
    def closing_soon(self):
        now = timezone.now()
        return now < self.deadline <= now + timedelta(days=1)

    def __str__(self):
        return self.title

class Comment(models.Model):
    listing = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments_made')
    title = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.listing.title}"
