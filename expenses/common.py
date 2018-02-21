from expenses.models import Category

UNTAGGED_SUBCATEGORY_TEXT = 'No Tagging'
ANYTEXT_CONTAINS_RULE_TEXT = 'Any Text Contains'


def get_untagged_category(user):
    untagged_category = Category.objects.get(owner=user, text=UNTAGGED_SUBCATEGORY_TEXT)
    return untagged_category
