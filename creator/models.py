from django.db import models


class Subscription(models.Model):
    email = models.EmailField()
    first_send_date = models.DateField()
    next_send_date = models.DateField()

    def __str__(self):
        return '{} - day {}'.format(self.email, self.next_send_date)