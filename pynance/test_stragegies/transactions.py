"""
Contains transaction test strategies.
"""

import hypothesis.strategies as st 
import datetime
import pandas as pd
import numpy as np

KNOWN_CURRENCIES = ['EUR', 'USD']
ALPHABET = list(map(str, 'abcdefghijklmnopqrstuvwzyz ABCDEFGHIJKLMNOPQRSTUVWZYZ0123456789äüöß'))

@st.composite
def single_transaction(draw, min_date=None, max_date=None):
    if not min_date:
        min_date = datetime.date(1000,1,1)
    if not max_date:
        max_date = datetime.date(9999,12,31)

    date = np.datetime64(draw(st.dates(min_value=min_date, max_value=max_date)))
    sender_account = draw(st.text(alphabet=ALPHABET))
    receiver_account = str(draw(st.text(alphabet=ALPHABET)))
    text = str(draw(st.text(alphabet=ALPHABET)))
    amount = draw(st.floats(min_value=0.01, max_value=10000000))
    total_balance = draw(st.floats(min_value=0.01, max_value=10000000))
    currency = str(draw(st.sampled_from(KNOWN_CURRENCIES)))
    category = str(draw(st.text(alphabet=ALPHABET)))
    tags = str(draw(st.text(alphabet=ALPHABET)))
    origin = str(draw(st.text(alphabet=ALPHABET)))

    return (date, sender_account, receiver_account, text, amount, total_balance, currency, category, tags, origin)

@st.composite
def dataframe(draw, min_size=0, max_size=None, min_date=None, max_date=None):
    elements = draw(st.lists(
        single_transaction(min_date=min_date, max_date=max_date),
         min_size=min_size,
         max_size=max_size
    ))

    dates, sender_accounts, receiver_accounts, texts, amounts, total_balances, currencies, \
        categories, tagss, origins = [],[],[],[],[],[],[],[],[],[]

    for date, sender_account, receiver_account, text, amount, total_balance, currency, category, tags, origin in elements:
        dates.append(date)
        sender_accounts.append(sender_account)
        receiver_accounts.append(receiver_account)
        texts.append(text)
        amounts.append(amount)
        total_balances.append(total_balance)
        currencies.append(currency)
        categories.append(category)
        tagss.append(tags)
        origins.append(origin)


    return pd.DataFrame({
        'date': dates,
        'sender_account': sender_accounts,
        'receiver_account': receiver_accounts,
        'text': texts,
        'amount': amounts,
        'total_balance': total_balances,
        'currency': currencies,
        'category': categories,
        'tags': tagss,
        'origin': origins
    })