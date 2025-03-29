from django.db import models
import uuid
'''
python manage.py makemigrations
python manage.py migrate
'''

class Patient(models.Model):
    record_id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    basic_items = models.JSONField(null=True)
    patient_ch_summary = models.TextField(null=True)
    patient_en_summary = models.TextField(null=True)
    doctor_modified_summary = models.TextField(null=True)
    conversation = models.JSONField(null=True)
    sick_leave = models.CharField(max_length=8, null=True)
    referral_letter = models.CharField(max_length=8, null=True)
    asr_text = models.TextField(null=True)
    medical_record = models.TextField(null=True)

class TentativeMap(models.Model):
    patient_id = models.AutoField(primary_key=True)
    record_id = models.ForeignKey(Patient, on_delete=models.CASCADE)