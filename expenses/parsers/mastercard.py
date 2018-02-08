from datetime import datetime

import pandas as pd

from expenses.models import Transaction
from expenses.parsers.abstract import get_add_source, get_subcategory


class MastercardParser(object):

    def get_transactions(self, file, user):
        source_type_name = 'Mastercard'
        table = pd.read_excel(file).to_dict('records')
        source_type_id = str(table[1][(list(table[1].keys())[0])].split(' ')[-1])
        source = get_add_source(user=user, source_type_name=source_type_name, source_type_id=source_type_id)
        transactions = []
        file.file.seek(0)
        table = pd.read_excel(file, skiprows=5).to_dict('records')
        for row in table:

            if str(row['תאריך רכישה']) == 'nan':
                break
            date = datetime.strptime(str(row['תאריך רכישה']), '%d/%m/%Y')
            merchant = row['שם בית עסק']
            comment = ''
            if str(row['פירוט נוסף']) != 'nan':
                comment = str(row['פירוט נוסף'])
            amount = float(row['סכום חיוב'])
            transaction = Transaction(comment=comment, merchant=merchant, date=date, amount=amount, source=source,
                                      subcategory=get_subcategory(user=user, comment=comment, merchant=merchant),
                                      owner=user)
            transactions.append(transaction)
        return transactions


    def is_me(self, file):
        try:
            table = pd.read_excel(file).to_dict('records')
            if 'מסטרקארד' in table[1][(list(table[1].keys())[0])]:
                card_number = table[1][(list(table[1].keys())[0])].split(' ')[-1]
                return True
            else:
                return False

        except Exception as e:
            return False

