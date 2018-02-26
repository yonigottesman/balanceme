from datetime import datetime

import pandas as pd

from expenses.models import Transaction
from expenses.parsers.abstract import get_add_source, get_subcategory


class LeumicardParser(object):

    def get_transactions(self, file, user):
        try:
            source_type_name = 'Leumicard'
            source_type_id = ''
            source = get_add_source(user=user, source_type_name=source_type_name, source_type_id=source_type_id)
            transactions = []
            file.file.seek(0)
            table = pd.read_excel(file).to_dict('records')
            for row in table:
                date = datetime.strptime(str(row['תאריך עסקה']), '%d/%m/%Y')
                merchant = row['שם בית העסק']
                comment = ''
                if str(row['הערות']) != 'nan':
                    comment = str(row['הערות'])
                amount = float(row['סכום חיוב ₪'])


                subcategory = get_subcategory(user=user, comment=comment, merchant=merchant)
                if subcategory is not None:
                    transaction = Transaction.create(comment=comment, merchant=merchant, date=date, amount=amount,
                                                     source=source,
                                                     subcategory=subcategory, user=user)
                    transactions.append(transaction)

            return transactions
        except Exception as e:
            return []

    def is_me(self, file):
        try:
            table = pd.read_excel(file).to_dict('records')
            headlines = list(table[0].keys())
            if len(headlines) != 8:
                return False
            if headlines[0] != 'תאריך עסקה':
                return False
            if headlines[1] != 'תאריך חיוב':
                return False
            if headlines[2] != 'שם בית העסק':
                return False
            if headlines[3] != 'סוג עסקה':
                return False
            if headlines[4] != 'מטבע עסקה' and headlines[4] != 'סכום מקור':
                return False
            if headlines[5] != 'סכום עסקה' and headlines[5] != 'מטבע מקור':
                return False
            if headlines[6] != 'סכום חיוב ₪':
                return False
            if headlines[7] != 'הערות':
                return False
            return True

        except Exception as e:
            return False


