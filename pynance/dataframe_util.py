from .definitions import COLUMNS
from hashlib import md5


def hash_row(row):
    h = md5()
    for value in row:
        h.update(bytes(str(value), encoding='utf8'))
    return h.hexdigest()


def create_id_hash(new_df):
    return new_df.apply(hash_row, axis=1)
