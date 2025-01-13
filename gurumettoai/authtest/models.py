from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class LikedRestaurant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_restaurants')
    restaurant_name = models.CharField(max_length=255)
    restaurant_address = models.TextField()
    liked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.restaurant_name} liked by {self.user.username}"
