from datetime import datetime
import sys

from bs4 import BeautifulSoup

from .abstract import get_add_source, create_transaction


class LeumiBankCardsParser(object):
    ignore_visa_transactions = True
    visa_transaction_merchants = ['ל.מסטרקארדי']

    def is_visa_transaction(self, merchant):
        if merchant in self.visa_transaction_merchants:
            return True
        return False

    def get_transactions(self, file, user):
        try:
            html = file.read()
            parsed_html = BeautifulSoup(html, "html.parser")
            transactions = []
            tables = parsed_html.find_all(class_='dataTable')
            for table in tables:
                for row in table.findChildren('tr'):
                    cols = list(row.findChildren('td'))
                    if len(cols) != 8:
                        continue
                    comment = ''
                    date = cols[1].get_text()
                    if date == '\xa0':
                        continue

                    date = datetime.strptime(cols[1].get_text(), '%d/%m/%y')
                    merchant = cols[2].get_text()
                    amount = float(cols[4].get_text().replace(',', ''))
                    card = cols[3].get_text()
                    source = get_add_source(user=user, source_type_name=card, source_type_id='')

                    transaction = create_transaction(comment=comment, merchant=merchant, date=date, amount=amount,
                                                     source=source, user=user)
                    if transaction is not None:
                        transactions.append(transaction)

        except Exception as e:
            sys.stderr.write(e)
            return None

        return transactions

    def is_me(self, file):
        try:
            html = file.read()
            parsed_html = BeautifulSoup(html, "html.parser")
            leumi = parsed_html.find_all(class_='PageTitle')[0].get_text()
            if leumi == 'בנק לאומי - פירוט חיובים בכרטיס אשראי':
                return True
        except Exception:
            return False


