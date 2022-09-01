import inquirer

# text
# questions = [
#     inquirer.Text('name', message="What's your name"),
#     inquirer.Text('surname', message="What's your surname"),
#     inquirer.Text('phone', message="What's your phone number",
#                   validate=lambda _, x: re.match('\+?\d[\d ]+\d', x),
#                   )
# ]
# answers = inquirer.prompt(questions)
# print(answers)
# {'name': 'wee', 'surname': 'ewe', 'phone': '123445'}


# editor
# questions = [
#   inquirer.Editor('long_text', message="Provide long text")
# ]
# answers = inquirer.prompt(questions)
# print(answers)
# editor.EditorError: Unable to find a viable editor on this system.Please consider setting your $EDITOR variable

# List
# questions = [
#   inquirer.List('size',
#                 message="What size do you need?",
#                 choices=['Jumbo', 'Large', 'Standard', 'Medium', 'Small', 'Micro'],
#             ),
# ]
# answers = inquirer.prompt(questions)
# print(answers)
# {'size': 'Standard'}

# checkbox
questions = [
    inquirer.Checkbox('interests',
                      message="What are you interested in?",
                      choices=['Computers', 'Books', 'Science', 'Nature', 'Fantasy', 'History'],
                      ),
]
answers = inquirer.prompt(questions)
print(answers)
# {'interests': []} why []?
