from django.contrib import admin

# Register your models here.
from apps.users.models import (TwilloResponseData,UserDataTable,UserConfirmationCode)

admin.site.register(TwilloResponseData)
admin.site.register(UserDataTable)
admin.site.register(UserConfirmationCode)
