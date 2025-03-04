from django.db import models
from users.models import CustomUser, UserRoles
import datetime

import logging
logger = logging.getLogger(__name__)

class PartnerType:
    CUSTOMER = 'customer'
    VENDOR = 'vendor'
    
    CHOICES = (
        (CUSTOMER, 'Customer'),
        (VENDOR, 'Vendor'),
    )

class PartnerProfile(models.Model):
    profile_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    partner_type = models.CharField(max_length=20, choices=PartnerType.CHOICES, default=PartnerType.CUSTOMER)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    secondary_contact = models.CharField(max_length=15, blank=True, null=True)
    
    created_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_partners'
    )
    updated_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='updated_partners'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.profile_id} - {self.company_name or f'{self.first_name} {self.last_name}'}"
    
    def save(self, *args, **kwargs):
        if not self.profile_id:
            today = datetime.date.today().strftime('%Y%m%d')
            prefix = "CUS" if self.partner_type == PartnerType.CUSTOMER else "VEN"
            
            last_profile = PartnerProfile.objects.filter(
                profile_id__startswith=f'{prefix}{today}'
            ).order_by('profile_id').last()
            
            if last_profile and last_profile.profile_id and last_profile.profile_id[len(prefix)+8:].isdigit():
                new_sequence = str(int(last_profile.profile_id[len(prefix)+8:]) + 1).zfill(4)
            else:
                new_sequence = '0001'
                
            self.profile_id = f'{prefix}{today}{new_sequence}'
        
        super().save(*args, **kwargs)