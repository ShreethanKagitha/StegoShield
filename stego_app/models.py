from django.db import models

class StegoStats(models.Model):
    OPERATION_CHOICES = [
        ('ENCODE', 'Encoding'),
        ('DECODE', 'Decoding'),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True)
    operation = models.CharField(max_length=10, choices=OPERATION_CHOICES)
    image_size_bytes = models.IntegerField()
    message_length = models.IntegerField(default=0)
    psnr = models.FloatField(null=True, blank=True)
    mse = models.FloatField(null=True, blank=True)
    processing_time_ms = models.FloatField()
    success = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.operation} at {self.timestamp}"
