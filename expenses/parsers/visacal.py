from expenses.models import Transaction
from .abstract import FileParser
import dateutil.parser

class VisaCalParser(FileParser):

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
        decoded_file = file.decode('utf-16')
        source = "visa " + decoded_file.split("\n")[1].split("המסתיים בספרות")[1].split(",")[0]
        for line in decoded_file.split('\n'):
            transaction = self.parse_transaction(line, source=source)
            if transaction != None:
                transactions.append(transaction)

        return transactions
