import basic


while True:
    text = input('basic > ')
    value, error = basic.run('<stdin>', text)

    if error: print(error.as_string())
    else: print(value)
