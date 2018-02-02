from expenses.models import InputSource, Transaction, Category, SubCategory


class FileParser(object):

    def __init__(self):
        from .visacal import VisaCalParser
        from .poalimbank import PoalimBankParser

        self.parsers = [VisaCalParser(), PoalimBankParser()]

    def factory(self, file):

        for parser in self.parsers:
            file.file.seek(0)
            if parser.is_me(file):
                file.file.seek(0)
                return parser

        return None


def get_add_source(source_type_name, source_type_id):
    try:
        source = InputSource.objects.get(type_name=source_type_name, type_id=source_type_id)
    except InputSource.DoesNotExist:
        source = InputSource(type_name=str(source_type_name), type_id=str(source_type_id))
        source.save()

    return source


# TODO check efficiency of this function
def remove_existing(new_transactions):
    if len(new_transactions) is 0:
        return new_transactions

    without_duplicates = []
    for transaction in new_transactions:

        found = Transaction.objects\
            .filter(comment=transaction.comment)\
            .filter(merchant=transaction.merchant)\
            .filter(amount=transaction.amount)\
            .filter(source=transaction.source)\
            .filter(date=transaction.date)

        if len(found) == 0:
            without_duplicates.append(transaction)

    return without_duplicates

def get_untagged_subcategory():
    subcategory = SubCategory.objects.get(text="UnTagged")
    return subcategory
