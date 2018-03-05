from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse

from expenses.common import UNTAGGED_SUBCATEGORY_TEXT
from expenses.models import Category, SubCategory, RuleType, Rule

DEFAULT_CATEGORIES = {'Supplies': ['Groceries', 'Cosmetics'],
                      'Recreational':['Restaurants', 'Going Out', 'Books/Games/Apps', 'Treats'],
                      'Bills': ['Gas/Electricity/Water', 'Internet/Cellular/TV'],
                      'Housing': ['House Committee', 'Rent','Property Tax'],
                      'Education': ['Higher Education'],
                      'Fitness': ['Sport Class'],
                      'Cash Withdraw':['Cash Withdraw'],
                      'Clothing': ['Clothing'],
                      'House Stuff': ['Electronics', 'Furniture', 'House Stuff'],
                      'Vacation': ['Vacation'],
                      'Other': ['Presents', 'Other'],
                      'Services': ['Services'],
                      'Transportation': ['Private Car', 'Public Transportation'],
                      'Kids': ['Kids Clothing', 'Daycare', 'Kids Toys and Gear'],
                      'Medical': ['Medical Insurance'],
                      UNTAGGED_SUBCATEGORY_TEXT: [UNTAGGED_SUBCATEGORY_TEXT], # TODO disable user using this string
                      'Investments': ['Stocks']}

DEFAULT_ALL_CONTAINS_RULES = {'Groceries': ['שופרסל', 'מינימרקט','ניצת הדובדבן','מאפיית', 'סופר פארם'],
                              'Restaurants': ['ויוינו', 'סינטה בר', 'קפה לואיז', 'אייססלון', 'רולדין', 'קפאין', 'מנדרין'],
                              'Gas/Electricity/Water': ['חברת החשמל','סופרגז'],
                              'Internet/Cellular/TV': ['netflix', 'פרטנר', 'הוט נט'],
                              'Kids Clothing': ['next', 'carters'],
                              'Medical Insurance': ['כללית'],
                              'Private Car': ['פז', 'סונול', 'דלק', 'כביש 6', 'פנגו'],
                              'Public Transportation': ['TTEG', 'רכבת'],
                              'Furniture': ['ikea'],
                              'Electronics': ['LASTPRICE'],
                              'Kids Toys and Gear': ['שילב'],
                              }


def create_user_defaults(user):
    for category in DEFAULT_CATEGORIES:
        category_object = Category(text=category, owner=user)
        category_object.save()
        for subcategory in DEFAULT_CATEGORIES[category]:
            subcategory_object = SubCategory(text=subcategory, category=category_object, owner=user)
            subcategory_object.save()

    rule_type = None #RuleType.objects.get(text='Any Text Contains')
    for subcategory in DEFAULT_ALL_CONTAINS_RULES:
        subcategory_object = SubCategory.objects.get(owner=user, text=subcategory)
        for value in DEFAULT_ALL_CONTAINS_RULES[subcategory]:
            rule = Rule(rule_type=rule_type,value=value, subCategory=subcategory_object, owner=user)
            rule.save()


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            create_user_defaults(user)
            return redirect(reverse('expenses:index'))
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})