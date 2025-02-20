from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)  
    description = models.TextField(blank=True, null=True) 
    is_active = models.BooleanField(default=True)  

    def __str__(self):
        return self.name
    
class Service(models.Model):

    COUNTRY_CHOICES = (
        ("india", "India"),
        ("saudi", "Saudi Arabia"),
    )

    VAT_CHOICES = (
        ("standard", "Standard VAT (15%)"),
        ("zero_rated", "Zero-Rated VAT (0%)"),
        ("exempt", "Exempt VAT (No VAT applied)"),
    )

    TAX_CHOICES = (
        ("GST_5", "5% GST"),
        ("GST_12", "12% GST"),
        ("GST_18", "18% GST"),
        ("GST_28", "28% GST"),
        ("none", "No Tax"),
    )

    TAX_CODES =(
        ("HSN", "HSN"),
        ("HS", "HS"),   
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)  
    # offer_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, default=None, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    service_type = models.CharField(max_length=20)  
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="services")
    is_active = models.BooleanField(default=True) 

    country = models.CharField(max_length=10, choices=COUNTRY_CHOICES, default="saudi")
    tax_codes= models.CharField(max_length=10, choices=TAX_CODES, default="HS")

    #GST Field (Only for India)
    gst_type = models.CharField(max_length=10, choices=TAX_CHOICES, default="none")
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15)  
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)

    # VAT Field (Only for Saudi Arabia)
    vat_type = models.CharField(max_length=20, choices=VAT_CHOICES, default="standard")
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15)  
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    


    def save(self, *args, **kwargs):
        """
        Override save method to calculate VAT and GST amounts dynamically.
        """

        taxable_amount = self.offer_price if self.offer_price else self.price

        if self.country == "india":
            tax_rates = {
                "GST_5": 5,
                "GST_12": 12,
                "GST_18": 18,
                "GST_28": 28,
                "none": 0,
            }
            self.gst_rate = tax_rates.get(self.gst_type, 0)
            self.gst_amount = (taxable_amount * self.gst_rate) / 100
            self.vat_amount = 0  # VAT not applicable in India

        elif self.country == "saudi":
            vat_rates = {
                "standard": 15,
                "zero_rated": 0,
                "exempt": 0,
            }
            self.vat_rate = vat_rates.get(self.vat_type, 0)
            self.vat_amount = (taxable_amount * self.vat_rate) / 100
            self.gst_amount = 0  # GST not applicable in Saudi
        self.total_price = taxable_amount + self.vat_amount  
        
        super(Service, self).save(*args, **kwargs)


