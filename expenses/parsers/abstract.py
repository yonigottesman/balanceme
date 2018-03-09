from expenses.common import get_untagged_subcategory
from expenses.models import InputSource, Transaction, Rule


class FileParser(object):

    def __init__(self):
        from .visacal import VisaCalParser
        from .poalimbank import PoalimBankParser
        from .mastercard import MastercardParser
        from .leumicard import LeumicardParser
        from expenses.parsers.leumibabk import LeumiBankParser
        from expenses.parsers.LeumiBankCards import LeumiBankCardsParser
        self.parsers = [VisaCalParser(), PoalimBankParser(), MastercardParser(),
                        LeumicardParser(), LeumiBankParser(),LeumiBankCardsParser()]

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


def rule_applies(rule, transaction):

    if rule.value is not None:
        if not (rule.value.lower() in transaction.merchant.lower() or rule.value.lower() in transaction.comment.lower()):
            return False

    if rule.source is not None:
        if transaction.source != rule.source:
            return False

    if rule.amount is not None:
        if transaction.amount != rule.amount:
            return False

    if rule.day is not None:
        if transaction.date.day != rule.day:
            return False

    return True


# return None means delete
def get_subcategory(transaction):
    all_rules = Rule.objects.filter(owner=transaction.owner)
    for rule in all_rules:
        if rule_applies(rule, transaction=transaction):
            return rule.subCategory

    untagged_subcategory = get_untagged_subcategory(transaction.owner)
    return untagged_subcategory


def create_transaction(comment, merchant, date, amount, source, user):
    transaction = Transaction(comment=comment, merchant=merchant.replace('\'', ''), date=date, amount=amount,
                              source=source, subcategory=None, owner=user)

    subcategory = get_subcategory(transaction)
    if subcategory is not None:
        transaction.subcategory = subcategory
        return transaction
    else:
        return None
