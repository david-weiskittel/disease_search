from django.db import models

# Create basic models to store conditions and symptoms, and link them to each other
class Condition(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Symptom(models.Model):
    name = models.CharField(max_length=200)
    conditions = models.ManyToManyField(Condition)

    def __str__(self):
        return self.name

class ConditionCount(models.Model):
    count = models.IntegerField()
