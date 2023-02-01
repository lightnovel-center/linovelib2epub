import inquirer

questions = [
    inquirer.List('size',
                  message="What size do you need?",
                  choices=[('Jumbo',1), ('Large',2),],
                  ),
]
# answers = inquirer.prompt(questions)
# print(answers)


questions = [
  inquirer.Checkbox('interests',
                    message="What are you interested in?",
                    choices=[('Jumbo',1), ('Large',2)], ),
]
answers = inquirer.prompt(questions)
print(answers['interests'])