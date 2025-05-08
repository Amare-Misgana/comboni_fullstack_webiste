import string
import secrets
import re



def generate_password(length=8, include_uppercase=True, include_digits=True, include_special_chars=True):
    lowercase_letters = string.ascii_lowercase
    uppercase_letters = string.ascii_uppercase if include_uppercase else ''
    digits = string.digits if include_digits else ''
    special_chars = string.punctuation if include_special_chars else ''
    all_chars = lowercase_letters + uppercase_letters + digits + special_chars
    password = ''.join(secrets.choice(all_chars) for _ in range(length))
    return password




def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    if not re.match(email_regex, email):
        return False
    return True