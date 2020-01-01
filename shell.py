import basic


while True:
    text = input('basic > ')
    tokens, error = basic.run('<stdin>', text)

    if error: print(error.as_string())
    else: print(tokens)
