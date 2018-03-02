from expenses.common import UNTAGGED_SUBCATEGORY_TEXT
from expenses.models import InputSource, Transaction, SubCategory, Rule



class FileParser(object):

    def __init__(self):
        from .visacal import VisaCalParser
        from .poalimbank import PoalimBankParser
        from .mastercard import MastercardParser
        from .leumicard import LeumicardParser
        from expenses.parsers.leumibabk import LeumiBankParser
        from expenses.parsers.LeumiBankCards import LeumiBankCardsParser
        self.parsers = [VisaCalParser(), PoalimBankParser(), MastercardParser(), LeumicardParser(), LeumiBankParser(),LeumiBankCardsParser()]

    def factory(self, file):

        for parser in self.parsers:
            file.file.seek(0)
            if parser.is_me(file):
                file.file.seek(0)
                return parser

        return None


def get_add_source(user, source_type_name, source_type_id):
    try:
        source = InputSource.objects.get(owner=user, type_name=source_type_name, type_id=source_type_id)
    except InputSource.DoesNotExist:
        source = InputSource(owner=user, type_name=str(source_type_name), type_id=str(source_type_id))
        source.save()

    return source


# TODO check efficiency of this function
def remove_existing(new_transactions):
    if len(new_transactions) is 0:
        return new_transactions

    without_duplicates = []
    for transaction in new_transactions:

        found = Transaction.objects \
            .filter(owner=transaction.owner) \
            .filter(comment=transaction.comment)\
            .filter(merchant=transaction.merchant)\
            .filter(amount=transaction.amount)\
            .filter(source=transaction.source)\
            .filter(date=transaction.date)

        if len(found) == 0:
            without_duplicates.append(transaction)

    return without_duplicates


def rule_applies(rule, merchant, comment):
    #if rule.rule_type.text == ANYTEXT_CONTAINS_RULE_TEXT:
    if rule.value.lower() in merchant.lower() or rule.value.lower() in comment.lower():
        return rule.subCategory


def get_subcategory(user, merchant, comment):
    rules = Rule.objects.filter(owner=user)
    for rule in rules:
        if rule_applies(rule, merchant, comment):
            return rule.subCategory

    untagged_subcategory = SubCategory.objects.get(owner=user, text=UNTAGGED_SUBCATEGORY_TEXT)
    return untagged_subcategory
