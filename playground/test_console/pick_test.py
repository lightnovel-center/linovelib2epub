from pick import pick

title = 'Please choose your favorite programming language: '
options = ['Java', 'JavaScript', 'Python', 'PHP', 'C++', 'Erlang', 'Haskell']
option, index = pick(options, title)
print(option)
print(index)

# cons 1: Redirection is not supported.
# cons 2: it uses curses and opens up a new simple GUI, NOT succinct.
