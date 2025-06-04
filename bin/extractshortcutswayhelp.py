#!/usr/bin/python3
import os

def extractShortcuts(filename="~/.config/sway/keys.sway"):
    """
    Extract keyboard shortcuts from a Sway configuration file.

    Reads a Sway configuration file and extracts keyboard shortcuts with their
    descriptions. The file format expects lines starting with "#- " followed
    by a description, then the next line containing the key binding command.

    Args:
        filename (str): Path to the Sway configuration file.
                       Defaults to "~/.config/sway/keys.sway".

    Examples:
        >>> import tempfile
        >>> import os
        >>> # Create a test config file
        >>> test_content = '''#- Open terminal
        ... bindsym $mod+Return exec $term
        ... #- Close window
        ... bindsym --locked $mod+Shift+q kill
        ... # Regular comment (ignored)
        ... bindsym $mod+d exec $menu'''
        >>>
        >>> with tempfile.NamedTemporaryFile(mode='w', suffix='.sway', delete=False) as f:
        ...     f.write(test_content)
        ...     temp_file = f.name
        >>>
        >>> # Test the function (would normally print output)
        >>> lines = extractShortcuts(temp_file)  # Would print sorted shortcuts
        >>> "Open terminal: $mod+Return" in lines
        True
        >>> "Close window: $mod+Shift+q" in lines
        True
        >>> # Clean up
        >>> os.unlink(temp_file)

        The string has the following format:
        "Description: key_combination"

        For the above example, when using `print`, it would output:
        Close window: $mod+Shift+q
        Open terminal: $mod+Return
    """
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
        return "\n".join(output)


if __name__ == "__main__":
    home_dir = os.getenv("HOME")
    join_lines = extractShortcuts(f"{home_dir}/.config/sway/keys.sway")
    print(join_lines)
