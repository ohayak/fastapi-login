import random


def get_random_readable_short_id(length=10) -> str:
    alphabet = "23456789abcdefghjkmnpqrstuvwxyz"
    return "".join(random.choices(alphabet, k=length))
