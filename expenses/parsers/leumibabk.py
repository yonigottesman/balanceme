from datetime import datetime
import sys

from bs4 import BeautifulSoup


from .abstract import get_add_source, create_transaction


class LeumiBankParser(object):
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
            source_type_name = 'Leumi Bank'
            source_type_id = parsed_html.find_all(class_="exportDataFilterForPrint")[0].find_all('tr')[0]\
                .find_all('td')[0].find_all('span')[6].get_text()
            source = get_add_source(user=user, source_type_name=source_type_name, source_type_id=source_type_id)

            transactions = []

            table = parsed_html.find(id='ctlActivityTable')
            for row in table.find_all(class_='ExtendedActivity_ForPrint'):

                amount = (row.find_all(class_='AmountDebitUniqeClass')[0].get_text().strip())
                if amount == '':
                    continue
                else:
                    amount = float(amount.replace(',', ''))

                date = row.find_all(class_='ExtendedActivityColumnDate')[0].get_text().strip()
                date = datetime.strptime(date, '%d/%m/%y')

                merchant = row.find_all(class_='ActivityTableColumn1LTR')
                if len(merchant) == 0:
                    merchant = row.find_all(class_='ActivityTableColumn1')[0].find_all('a')[0].get_text().strip()
                else:
                    merchant = merchant[0].get_text().strip()
                comment = ''

                transaction = create_transaction(comment=comment, merchant=merchant, date=date, amount=amount,
                                                 source=source, user=user)
                if transaction is not None:
                    transactions.append(transaction)

        except Exception as e:
            sys.stderr.write(str(e))
            return None

        return transactions

    def is_me(self, file):
        try:
            html = file.read()
            parsed_html = BeautifulSoup(html, "html.parser")
            bank_line = parsed_html.find_all(class_='PageTitle')[0].get_text()


            if bank_line == 'בנק לאומי - תנועות בחשבון':
                return True
        except Exception:
            return False


