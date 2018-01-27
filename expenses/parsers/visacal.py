from expenses.models import Transaction, InputSource
import dateutil.parser

from expenses.parsers.abstract import get_add_source


class VisaCalParser(object):

    def get_date(self, str):
        try:
            date = dateutil.parser.parse(str, dayfirst=True)
        except Exception:
            return None
        else:
            return date

    def parse_transaction(self, line, source):
        if len(line.split("\t")) != 4 and len(line.split("\t")) != 5:
            return None

        date = self.get_date(line.split("\t")[0])
        if date == None:
            return None

        merchant = line.split("\t")[1]
        amount = line.split("\t")[3].split("₪")[0].replace(',','')
        if '-' in amount:
            amount = '-' + amount.replace('-','')

        comment = ""
        if len(line.split("\t")) == 5:
            comment = line.split("\t")[4]

        return Transaction(comment=comment, merchant=merchant, date=date, amount=amount, source=source)

    def get_transactions(self, file):
        transactions = []
        decoded_file = file.read().decode('utf-16')
        source_type = "visa"
        source_type_id = str(decoded_file.split("\n")[1].split("המסתיים בספרות")[1].split(",")[0])
        source = get_add_source(source_type_name=source_type, source_type_id=source_type_id)
        for line in decoded_file.split('\n'):
            transaction = self.parse_transaction(line, source=source)
            if transaction != None:
                transactions.append(transaction)

        return transactions

    def is_me(self, file):
        try:
            decoded_file = file.read().decode('utf-16')
        except Exception:  # TODO catch decode error and not all
            return False
        if 'פירוט עסקות נכון לתאריך' not in decoded_file:
            return False
        if 'לכרטיס ויזה' not in decoded_file:
            return False
        if 'המסתיים בספרות' not in decoded_file:
            return False
        return True


