from django.db import models
from django.contrib.auth.models import User
import datetime
import pytz
from django.utils import timezone
from django.conf import settings

USER_TYPE_CHOICES = (

    ('ADM', ("Admin")),
    ('USR', ("Portal User")),
)

# Create your models here.
class TwilloResponseData(models.Model):
    from_phone_no = models.CharField(max_length=20, verbose_name='From Number',null=True,blank=True)
    to_phone_no = models.CharField(max_length=20, verbose_name='To Number',null=True,blank=True)
    message_sid = models.CharField(max_length=120, verbose_name='Message SID from Twillo',null=True,blank=True)
    date_send = models.DateTimeField(default=timezone.now,verbose_name='Message Created Date',null=True,blank=True)

    def __str__(self):
        return self.to_phone_no + " : " + str(self.date_send)

class UserDataTable(User):
    full_name = models.CharField(max_length=255,verbose_name='Full Name')
    phone_no = models.CharField(max_length=120,verbose_name='User Phone Number', null=True,blank=True,unique=True)
    active_date = models.DateTimeField(verbose_name='Activeted Date')
    trial_period = models.BooleanField(verbose_name='Trial period ?',default=True)
    user_type = models.CharField(choices=USER_TYPE_CHOICES, default='USR', max_length=3)
    
    def __str__(self):
        return self.full_name + " : " + str(self.active_date)

""" Confirmation Code for the User """
## Note: User will Unique
class UserConfirmationCode(models.Model):
    user = models.ForeignKey(UserDataTable)
    confirmation_code = models.CharField(max_length=255, verbose_name='Confirmation Code')
    message_sid = models.CharField(max_length=120, verbose_name='Message SID from Twillo',null=True,blank=True)
    date_created = models.DateTimeField(verbose_name='Date Created')
    is_used = models.BooleanField(default=False, verbose_name='Used ?')
    
    def __str__(self):
        return self.user.phone_no +" : " + self.confirmation_code

    def verfication_code_expired(self):
        if self.date_created:
            expired_date =  self.date_created + datetime.timedelta(seconds=settings.TOKEN_EXPIRES_SEC)
            return datetime.datetime.now(pytz.UTC) <= expired_date

