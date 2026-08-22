from django.contrib import admin
from .models import Admin, User, OriginalDocument, VerificationHistory, DigiLocker, Contact, UserDocument, Verification, Blockchain, ActivityLog

# Register your models here.
admin.site.register(Contact)
