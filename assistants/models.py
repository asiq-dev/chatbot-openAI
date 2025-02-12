from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)
    assistant_id = models.CharField(max_length=255, blank=True, null=True)
    thread_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    content = models.TextField()
    is_user = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]