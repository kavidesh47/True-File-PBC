from django.db import models

# -------------------------
# Admin Registration
# -------------------------
class Admin(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username


# -------------------------
# User Registration
# -------------------------
class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username


# -------------------------
# Original Documents
# -------------------------
class OriginalDocument(models.Model):

    document_name = models.CharField(max_length=200)

    document_type = models.CharField(max_length=100)

    uploaded_file = models.FileField(upload_to='original_documents/')

    sha256_hash = models.CharField(max_length=64)

    previous_hash = models.CharField(max_length=64, blank=True)

    block_hash = models.CharField(max_length=64)

    upload_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, default="Verified")

    def __str__(self):
        return self.document_name


# -------------------------
# Blockchain Ledger
# -------------------------
class Blockchain(models.Model):
    block_number = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    document_id = models.CharField(max_length=20)
    document_name = models.CharField(max_length=200)
    document_hash = models.CharField(max_length=64)
    previous_hash = models.CharField(max_length=64)
    current_hash = models.CharField(max_length=64)

    def __str__(self):
        return f"Block {self.block_number}"


# -------------------------
# Verification
# -------------------------
class Verification(models.Model):
    verification_id = models.CharField(max_length=20, unique=True)
    document_name = models.CharField(max_length=200)
    generated_hash = models.CharField(max_length=64)
    blockchain_hash = models.CharField(max_length=64)
    status = models.CharField(max_length=30)
    verified_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.verification_id


# -------------------------
# Verification History
# -------------------------
class VerificationHistory(models.Model):

    user_name = models.CharField(max_length=100)

    document_name = models.CharField(max_length=200)

    document_type = models.CharField(max_length=100)

    result = models.CharField(max_length=50)

    verified_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_name


# -------------------------
# DigiLocker
# -------------------------
class DigiLocker(models.Model):
 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    document_name = models.CharField(max_length=200)

    document_type = models.CharField(max_length=100)

    document_file = models.FileField(upload_to='digilocker/')

    uploaded_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.document_name
    def __str__(self):
        return self.document_name


# -------------------------
# Activity Logs
# -------------------------
class ActivityLog(models.Model):
    username = models.CharField(max_length=100)
    activity = models.CharField(max_length=300)
    activity_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

        # -------------------------
# User DigiLocker Documents
# -------------------------
class UserDocument(models.Model):

    user = models.ForeignKey( User, on_delete=models.CASCADE, null=True, blank=True )

    document_name = models.CharField(max_length=200)

    document_type = models.CharField(max_length=100)

    document_file = models.FileField(upload_to="digilocker/")

    uploaded_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.document_name


# -------------------------
# Contact Messages
# -------------------------
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name