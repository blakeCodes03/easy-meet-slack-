from django.db import models
from django.core.validators import MinValueValidator

class Api_response(models.Model):
    description = models.CharField(max_length=300)
    date = models.CharField(max_length=50, help_text='e.g "seo7days"')
    startTime = models.PositiveSmallIntegerField(default = 1, validators=[MinValueValidator(1)])
    endTime = models.PositiveSmallIntegerField(default = 30, validators=[MinValueValidator(10)]) # Minimum value is 10
    number_of_tabs_to_click_sponsored_links = models.PositiveSmallIntegerField(default = 1, validators=[MinValueValidator(1)])
    interval_between_each_round = models.PositiveSmallIntegerField(help_text = 'in hours')
    # turn_off_bot = models.BooleanField(default=False)
    

    def __str__(self):
        return self.description