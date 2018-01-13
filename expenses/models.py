from django.db import models


class Category(models.Model):
    text = models.CharField(max_length=200)
    def __str__(self):
        return self.text


class SubCategory(models.Model):
    text = models.CharField(max_length=200)
    catagory = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Transaction(models.Model):
    comment = models.CharField(max_length=200)
    merchant = models.CharField(max_length=200)
    date = models.DateField('Transaction date')
    amount = models.CharField(max_length=200)
    source = models.CharField(max_length=200)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.merchant


class KnownKeyWords(models.Model):
    txn_text_contains = models.CharField(max_length=200)
    subCatagory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)