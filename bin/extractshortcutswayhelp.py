#!/usr/bin/python3
import os


# Reads a file that expects the format
# #- Description of the shortcut
#
def extractShortcuts(filename="~/.config/sway/keys.sway"):
    with open(filename) as file:
        read_lines = file.readlines()
        current = 0
        nlines = len(read_lines)
        output = []
        while current < nlines:
            if not read_lines[current].startswith("#- "):
                current += 1
                continue
            if current + 1 >= nlines:
                break
            command = read_lines[current + 1].split(" ")

            if len(command) < 2:
                # The file is not formatted properly
                continue
            keys = command[1]
            if command[1] == "--locked":
                keys = command[2]
            output.append(f"{ read_lines[current][3:-1]}: {keys}")
            current += 2
        output.sort()
        print("\n".join(output))


if __name__ == "__main__":
    home_dir = os.getenv("HOME")
    extractShortcuts(f"{home_dir}/.config/sway/keys.sway")
