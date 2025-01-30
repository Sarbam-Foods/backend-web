from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

# Create your models here.
class Utility(models.Model):
   show_alert = models.BooleanField(default=True)
   photo = models.ImageField(upload_to='website/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=('jpg', 'jpeg' 'png'))])
   title = models.CharField(max_length=255, null=True, blank=True)
   subtitle = models.CharField(max_length=500, null=True, blank=True)
   whatsapp = models.URLField(null=True, blank=True)
   facebook = models.URLField(null=True, blank=True)
   instagram = models.URLField(null=True, blank=True)

   def __str__(self):
      return "Website Information"
   
   class Meta:
      verbose_name = "Utility"
      verbose_name_plural = "Utilities"

   def save(self, *args, **kwargs):
      if not self.pk and Utility.objects.exists():
         raise ValidationError("Another Utility cannot be added. Update the Website details!")
      return super().save(*args, **kwargs)
   

class ImageCarousel(models.Model):
   image1 = models.ImageField(upload_to='carousel/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'jpeg'))])
   image2 = models.ImageField(upload_to='carousel/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'jpeg'))])
   image3 = models.ImageField(upload_to='carousel/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'jpeg'))])

   def __str__(self):
      return "Edit your Carousel"
   
   def save(self, *args, **kwargs):
      if not self.pk and ImageCarousel.objects.exists():
         raise ValidationError("This cannot be added!")
      return super().save(*args, **kwargs)
   

class BaseModel(models.Model):
   created_at = models.DateTimeField(auto_now_add=True)

   class Meta:
      abstract = True


class PromoAd(BaseModel):
   promo_response = models.TextField()

   def __str__(self):
      return self.promo_response
   

class About(models.Model):
   main_text = models.TextField(null=True, blank=True)

   banner_photo = models.ImageField(upload_to='banner/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'jpeg'))])
   banner_photo2 = models.ImageField(upload_to='banner/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'jpeg'))])

   text1 = models.TextField(null=True, blank=True)
   text2 = models.TextField(null=True, blank=True)

   photo1 = models.ImageField(upload_to='photo/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'jpeg'))])
   photo2 = models.ImageField(upload_to='photo/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'jpeg'))])
   
   def __str__(self):
      return "Website Abouts"
   

   def save(self, *args, **kwargs):
      if not self.pk and About.objects.exists():
         raise ValidationError("This cannot be added!")
      return super().save(*args, **kwargs)
   