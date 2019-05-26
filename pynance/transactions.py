"""
Contains transaction test strategies.
"""

import hypothesis.strategies as st
import datetime
import pandas as pd
import numpy as np

from .dataframe_util import create_id_hash

KNOWN_CURRENCIES = ['EUR', 'USD']
ALPHABET = list(
    map(str, 'abcdefghijklmnopqrstuvwzyz ABCDEFGHIJKLMNOPQRSTUVWZYZ0123456789äüöß'))


@st.composite
def single_transaction(draw, min_date=None, max_date=None):

    # As a performance optimization, we don't generate each column individually and reuse
    # already generated values. If we don't do this, test generation is too slow and
    # Hypothesis' HealthChecks make the tests fail
    d = draw(st.dates(min_value=min_date, max_value=max_date))
    text = draw(st.text(alphabet=ALPHABET))
    floats = draw(st.floats(min_value=0.01, max_value=10000000))
    currency = draw(st.sampled_from(KNOWN_CURRENCIES))

    return (d, text, text, text, floats, floats, currency, text, text, text)


@st.composite
def dataframe(draw, min_size=0, max_size=None, min_date=None, max_date=None):
    if not min_date:
        min_date = datetime.date(1000, 1, 1)
    if not max_date:
        max_date = datetime.date(9999, 12, 31)

    elements = draw(st.lists(
        single_transaction(min_date=min_date, max_date=max_date),
        min_size=min_size,
        max_size=max_size
    ))

    dates, sender_accounts, receiver_accounts, texts, amounts, total_balances, currencies, \
        categories, tagss, origins = [], [], [], [], [], [], [], [], [], []

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

    result_frame = pd.DataFrame({
        'date': dates,
        'sender_account': sender_accounts,
        'receiver_account': receiver_accounts,
        'text': texts,
        'amount': amounts,
        'total_balance': total_balances,
        'currency': currencies,
        'category': categories,
        'tags': tagss,
        'origin': origins})

    hash_column = create_id_hash(result_frame)

    result_frame['id'] = hash_column

    return result_frame
