from datetime import datetime

from expenses.models import Category, SubCategory

UNTAGGED_SUBCATEGORY_TEXT = 'No Tagging'
ANYTEXT_CONTAINS_RULE_TEXT = 'Any Text Contains'


def get_untagged_category(user):
    untagged_category = Category.objects.get(owner=user, text=UNTAGGED_SUBCATEGORY_TEXT)
    return untagged_category

def get_untagged_subcategory(user):
    untagged_category = SubCategory.objects.get(owner=user, text=UNTAGGED_SUBCATEGORY_TEXT)
    return untagged_category

def get_datetime(date_str):
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except (ValueError, TypeError) as e:
        return None
    else:
        return date