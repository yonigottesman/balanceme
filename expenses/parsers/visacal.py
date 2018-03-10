
import dateutil.parser
import sys

from expenses.parsers.abstract import get_add_source, create_transaction


class VisaCalParser(object):

    def get_date(self, str):
        try:
            date = dateutil.parser.parse(str, dayfirst=True)
        except Exception:
            return None
        else:
            return date

    def parse_transaction(self, line, source, user):

        splits = line.split("\t")
        if len(splits) != 4 and len(splits) != 5:
            return None

        date = self.get_date(splits[0])
        if date == None:
            return None

        merchant = splits[1]
        amount = splits[3].replace("₪", '').replace(',', '').strip()
        
        if '-' in amount:
            amount = '-' + amount.replace('-','')
        amount = float(amount)
        comment = ""
        if len(splits) == 5:
            comment = line.split("\t")[4]

        tx = create_transaction(comment=comment, merchant=merchant, date=date, amount=amount, source=source, user=user)

        return tx

    def get_transactions(self, file, user):
        try:
            transactions = []
            decoded_file = file.read().decode('utf-16')
            source_type = "visa"
            source_type_id = str(decoded_file.split("\n")[1].split("המסתיים בספרות")[1].split(",")[0])
            source = get_add_source(user=user, source_type_name=source_type, source_type_id=source_type_id)

            for line in decoded_file.split('\n'):

                transaction = self.parse_transaction(line, source=source, user=user)
                if transaction != None:
                    transactions.append(transaction)

            return transactions

        except Exception as e:
            sys.stderr.write(str(e))
            return None


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


