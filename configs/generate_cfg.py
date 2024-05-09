import os

EXTENSION_PYTHON = '.py'
EXTENSION_CONFIG = '.cfg'
CONFIG = '''[Locations]
# Path to loadout config. Can use relative path from here.
looks_config = ../Appearance.cfg

# Path to python file. Can use relative path from here.
python_file = ../../src/{file_name}

# Name of the bot in-game
name = DreamMate {bot_name}

# The maximum number of ticks per second that your bot wishes to receive.
maximum_tick_rate_preference = 120

[Details]
# These values are optional but useful metadata for helper programs
# Name of the bot's creator/developer
developer = The RLBot community

# Short description of the bot
description = Your best teammate everrr!!! :D

# Fun fact about the bot
fun_fact = Your Dream Team

# Link to github repository
github = https://github.com/RLBot/RLBotPythonExample

# Programming language
language = python
'''


def main():
    path = '..\\src'
    list_files = os.listdir(path)
    for file_name in list_files:
        if file_name.endswith(EXTENSION_PYTHON) is False:
            continue
        bot_name = file_name.replace(EXTENSION_PYTHON, '')
        bot_config = CONFIG.format(file_name=file_name, bot_name=bot_name)
        config_path = '.\\rlbot\\' + bot_name + EXTENSION_CONFIG
        with open(config_path, 'w') as file:
            file.write(bot_config)
        print(bot_name, file_name, config_path)


if __name__ == '__main__':
    main()
