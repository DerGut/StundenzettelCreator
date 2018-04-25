from django.db import models

# Create your models here.


class Subscription(models.Model):
    send_date = models.DateField()
    send_frequency = models.DateField()
    email = models.EmailField()

    # TODO: Add all the other necessary items