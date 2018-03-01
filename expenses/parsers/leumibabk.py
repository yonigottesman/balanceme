from datetime import datetime

from expenses.models import Transaction
import pandas as pd
from .abstract import get_add_source, get_subcategory


class LeumiBankParser(object):
    ignore_visa_transactions = True
    visa_transaction_merchants = ['ל.מסטרקארדי']

    def is_visa_transaction(self, merchant):
        if merchant in self.visa_transaction_merchants:
            return True
        return False

    def get_transactions(self, file, user):
        try:
            source_type_name = 'Leumi Bank'
            tmp = pd.read_excel(file, skiprows=0).to_dict('records')
            source_type_id = list(tmp[2].values())[0].split('חשבון: ')[1]
            source = get_add_source(user=user, source_type_name=source_type_name, source_type_id=source_type_id)

            transactions = []
            file.file.seek(0)
            table = pd.read_excel(file, skiprows=21).to_dict('records')
        except Exception as e:
                return []

        for row in table:
            try:
                if str(row['חובה']) == 'nan':
                    continue

                if type(row['תאריך ']) == type('string'):
                    date =  datetime.strptime(row['תאריך '], '%d/%m/%y')
                else:
                    date = row['תאריך '].date()
                    if date.day <= 12:
                        tmp = date.day
                        date = date.replace(day=date.month)
                        date = date.replace(month=tmp)

                merchant = row['תיאור']
                if self.is_visa_transaction(merchant) and self.ignore_visa_transactions:
                    continue

                comment = ''
                amount = float(row['חובה'])

                subcategory = get_subcategory(user=user, comment=comment, merchant=merchant)
                if subcategory is not None:
                    transaction = Transaction.create(comment=comment, merchant=merchant, date=date, amount=amount,
                    source=source,
                    subcategory=subcategory, user=user)

                    transactions.append(transaction)

            except Exception:
                    continue
        return transactions

    def is_me(self, file):
        try:
            bank_line = list(pd.read_excel(file, skiprows=0).to_dict('records')[0].keys())[0]
            if bank_line == 'בנק לאומי - תנועות בחשבון':
                return True
        except Exception:
            return False


