import datetime
import string
import random
from django.utils import timezone
from django.db import models
from django.db.models import Q

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django import forms

# Create your models here.
class Venue(models.Model):
    venue_name = models.CharField(max_length=200, unique=True,)
    venue_capacity = models.IntegerField(max_length=200)
    code = models.SlugField(max_length=6, unique=True, editable=False) 

    def __str__(self):
        return "%s (%s)" % (self.venue_name, self.venue_capacity)
     
    def get_absolute_url(self):
        return reverse('venue-view', kwargs={'code': self.code})

    def genere(self, N):
        caracteres = string.ascii_letters + string.digits
        aleatoire = [random.choice(caracteres) for _ in range(N)]

        self.code = ''.join(aleatoire)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.genere(6)

        super(Venue, self).save(*args, **kwargs)

    def clean(self):
        sVenue = Venue.objects.all()

        if self.pk:
            sVenue = sVenue.exclude(pk=self.pk)

        sVenue = sVenue.filter(venue_name=self.venue_name)
        if sVenue.exists():
            raise forms.ValidationError("Venue already exists.")
 


now = datetime.datetime.now()
time_change = datetime.timedelta(0,1)  

PENDING = 'Pending'
ACCEPTED = 'Accepted'
CANCELLED = 'Cancelled'

class BookMeeting(models.Model):
    
     
    STATUS_OPTIONS = (
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (CANCELLED, 'Cancelled'),
    )
    book_date = models.DateField('Book Date', )
    from_time = models.TimeField('Start Time')   
    to_time = models.TimeField('End Time')           
    request_by = models.CharField(max_length=200)
    purpose = models.CharField(max_length=200)
    
    create_at = models.DateTimeField('Create Date', default=now)   # now.date()
    processed_at = models.DateTimeField('Processed Date', default=now)
    book_status = models.CharField(max_length=40, choices=STATUS_OPTIONS, default=PENDING)
    venue = models.ForeignKey(Venue)  # related_name='Book Venue'
    user = models.ForeignKey(User)    # related_name='Booked by User'

    def get_absolute_url(self):
        return reverse('meets-view', kwargs={'pk': self.id})

    def get_month_url(self, year, month):
        return reverse('meets-month', kwargs={'year': year, 'month': month})

    def get_day_url(self, year, month, day):
        return reverse('meets-day', kwargs={'year': year, 'month': month, 'day': day})

    def __str__(self):
        return "%s %s %s %s (%s) (%s)" % (self.book_date, str(self.from_time), str(self.to_time), self.venue.venue_name, 
                                                                                   self.venue.venue_capacity, self.user)

    class Meta:
        ordering = ["book_date", "from_time", ]

    def get_book_set(self):
        return BookMeeting.objects

    def clean(self):
        # Don't allow draft entries to have an error.
        #print (self.pk)
        #print (self.cleaned_data["id"])
        
        if not self.book_date or self.book_date < now.date():
            raise forms.ValidationError("You haven't set a valid Book date.")
        elif not self.to_time or not self.from_time or self.to_time <= self.from_time:
            raise forms.ValidationError("You haven't set a valid Time.") 
        elif not self.user.id:
            raise forms.ValidationError("Invalid user.") 
        elif not self.venue:
            raise forms.ValidationError("You haven't set a valid Venue.") 
        
        BooksMeet = BookMeeting.objects.exclude(pk=self.pk)
        BooksMeet = BooksMeet.filter(
                            Q(book_date=self.book_date,venue=self.venue),
                            Q(book_status='Pending') | Q(book_status='Accepted')
                            )
        
        if BooksMeet.exists():
            start_time = datetime.datetime.combine(self.book_date, self.from_time)
            end_time = datetime.datetime.combine(self.book_date, self.to_time)
            start_time = start_time + time_change
            end_time = end_time - time_change
            #8<6<10 || 8<7<10
            atBooksMeet = BooksMeet.filter(
                            Q(from_time__lte=start_time,to_time__gte=start_time) |
                            Q(from_time__lte=end_time,to_time__gte=end_time)
                            )
            if atBooksMeet.exists():
                raise forms.ValidationError("Time-slot is not available.")

        for inBooksMeet in BooksMeet:
            #1<3<5<12
            if self.from_time < inBooksMeet.from_time and self.to_time >  inBooksMeet.to_time:
                raise forms.ValidationError("Time-slot is not available. Do you want to continue?")

    
    def save(self, *args, **kwargs):
        super(BookMeeting, self).save(*args, **kwargs) # Call the "real" save() method.


