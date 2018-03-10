import io

import sys

from expenses.models import Transaction, InputSource
import pandas as pd
from .abstract import get_add_source, create_transaction


class PoalimBankParser(object):
    ignore_visa_transactions = True
    visa_transaction_merchants = ['ישראכרט','מסטרקרד','כרטיסי אשראי ל','לאומי קארד בע"','אמריקן אקספרס']

    def is_visa_transaction(self, merchant):
        if merchant in self.visa_transaction_merchants:
            return True
        return False

    def get_transactions(self, file, user):
        try:
            source_type_name = 'Poalim Bank'
            source_type_id = str(
                pd.read_excel(file.file, skiprows=3).to_dict('records')[0]['תנועות בחשבון'].split(' ')[3])
            source = get_add_source(user=user, source_type_name=source_type_name, source_type_id=source_type_id)
            transactions = []
            file.file.seek(0)
            table = pd.read_excel(file, skiprows=5).to_dict('records')

            for row in table:
                if str(row['חובה']) == 'nan':
                    continue
                date = row['תאריך ערך'].date()
                merchant = row['הפעולה']
                if self.is_visa_transaction(merchant) and self.ignore_visa_transactions:
                    continue
                if str(row['לטובת']) != 'nan':
                    merchant = merchant + ' ' + str(row['לטובת'])
                comment = ''
                if str(row['עבור']) != 'nan':
                    comment = str(row['עבור'])
                amount = float(row['חובה'])

                transaction = create_transaction(comment=comment, merchant=merchant, date=date, amount=amount,
                                                 source=source, user=user)
                if transaction is not None:
                    transactions.append(transaction)

            return transactions
        except Exception as e:
            sys.stderr.write(str(e))
            return None

    def is_me(self, file):
        try:
            bank_number = pd.read_excel(file, skiprows=3) \
            .to_dict('records')[0]['תנועות בחשבון'].split(' ')[3].split('-')[0]
        except Exception:
            return False
        else:
            if bank_number == '12':
                return True
            return False

