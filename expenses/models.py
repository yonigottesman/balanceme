from django.db import models


class Transaction(models.Model):
    txn_text = models.CharField(max_length=200)
    txn_date = models.DateTimeField('Transaction date')
    txn_tag = models.CharField(max_length=200)
    txn_amount = models.CharField(max_length=200)
    def __str__(self):
        return self.txn_text


class Choice(models.Model):
    question = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text




