from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    text = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class SubCategory(models.Model):
    text = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class InputSource(models.Model):
    type_name = models.CharField(max_length=50)
    type_id = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.type_name) + " " + str(self.type_id)


class Transaction(models.Model):
    comment = models.CharField(max_length=200)
    merchant = models.CharField(max_length=200)
    date = models.DateField('Transaction date')
    amount = models.FloatField()
    source = models.ForeignKey(InputSource, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.merchant


class RuleType(models.Model):
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text


class Rule(models.Model):
    rule_type = models.ForeignKey(RuleType, on_delete=models.CASCADE, null=True)
    value = models.CharField(max_length=200)
    subCategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
