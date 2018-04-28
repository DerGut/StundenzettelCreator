from django.db import models


class Subscription(models.Model):
    email = models.EmailField()
    first_send_date = models.DateField()
    next_send_date = models.DateField()
    hours = models.IntegerField()
    unit_of_organisation = models.CharField(max_length=250)
    name = models.CharField(max_length=300)
    first_name = models.CharField(max_length=200)

    def __str__(self):
        return '{} - day {}'.format(self.email, self.next_send_date)