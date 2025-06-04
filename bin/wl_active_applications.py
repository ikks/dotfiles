#!/usr/bin/python3
#
# Thanks to https://github.com/tobiaspc/wofi-scripts
#

from argparse import ArgumentParser
import subprocess
import json

# Available selectors, make sure you have the one you choose installed:
CMD_WOFI_SELECTOR = 'wofi -p "Windows: " -d -i --hide-scroll'
CMD_FUZZEL_SELECTOR = "fuzzel -R -d -b 000000D1 -w 50"
CMD_ROFI_SELECTOR = "rofi -dmenu window"
CMD_DMENU_SELECTOR = "dmenu -l 5"

# Pick your preferred selector
CMD_MENU_SELECTOR = CMD_FUZZEL_SELECTOR

ENTER = "\n"
CMD_SWAY_GET_WINDOW_INFO = "swaymsg -t get_tree"
CMD_SWAY_SET_ACTIVE_WINDOW = "swaymsg [con_id={}] focus"


def get_windows():
    """
    Get a list of all window objects from Sway's window tree.

    Retrieves window information by calling `swaymsg` and parsing the JSON response.
    Filters out inactive outputs.

    Returns:
        list: List of window dictionaries containing window information.

    Examples:
        >>> # Mock example - actual function calls swaymsg
        >>> windows = get_windows()
        >>> isinstance(windows, list)
        True
        >>> # Each window dict would contain keys like 'app_id', 'name', 'id'
    """

    process = subprocess.Popen(
        CMD_SWAY_GET_WINDOW_INFO,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    sway_output = process.communicate()[0]

    if process.returncode != 0:
        raise Exception(
            "Make sure you have swaymsg installed, verify with 'swaymsg -t get_tree'"
        )
    data = json.loads(sway_output)
    # Select outputs that are active
    windows = []
    for output in data["nodes"]:
        if output.get("type") == "output":
            workspaces = output.get("nodes")
            for ws in workspaces:
                if ws.get("type") == "workspace":
                    windows += extract_nodes_iterative(ws)
    return windows


def extract_nodes_iterative(workspace):
    """
    Extract all window nodes from a Sway workspace JSON object iteratively.

    Recursively processes workspace nodes to find all window objects,
    including both regular windows and floating windows.

    Args:
        workspace (dict): Sway workspace JSON object containing window nodes.

    Returns:
        list: List of all window node dictionaries found in the workspace.

    Examples:
        >>> # Mock workspace structure
        >>> workspace = {
        ...     'floating_nodes': [{'app_id': 'floating', 'name': 'Float'}],
        ...     'nodes': [
        ...         {'nodes': [], 'app_id': 'terminal', 'name': 'Terminal'},
        ...         {'nodes': [{'nodes': [], 'app_id': 'nested', 'name': 'Nested'}]}
        ...     ]
        ... }
        >>> nodes = extract_nodes_iterative(workspace)
        >>> len(nodes) >= 2  # At least floating and regular nodes
        True
    """
    all_nodes = []

    floating_nodes = workspace.get("floating_nodes")

    for floating_node in floating_nodes:
        all_nodes.append(floating_node)

    nodes = workspace.get("nodes")

    for node in nodes:
        # Leaf node
        if len(node.get("nodes")) == 0:
            all_nodes.append(node)
        # Nested node, handled iterative
        else:
            for inner_node in node.get("nodes"):
                nodes.append(inner_node)

    return all_nodes


def parse_windows(windows):
    """
    Parse window objects into formatted display strings.

    Converts window dictionaries into human-readable strings showing
    the application ID and window name in brackets format.

    Args:
        windows (list): List of window dictionaries with 'app_id' and 'name' keys.

    Returns:
        list: List of formatted window strings.

    Examples:
        >>> windows = [
        ...     {'app_id': 'firefox', 'name': 'Mozilla Firefox'},
        ...     {'app_id': 'terminal', 'name': 'Terminal Window'}
        ... ]
        >>> parsed = parse_windows(windows)
        >>> parsed[0]
        '[firefox] Mozilla Firefox'
        >>> parsed[1]
        '[terminal] Terminal Window'
    """
    parsed_windows = []
    for window in windows:
        parsed_windows.append(
            "[{}] {}".format(window.get("app_id"), window.get("name"))
        )
    return parsed_windows


def build_wofi_string(windows):
    """
    Build a UTF-8 encoded string of windows for menu display.

    Joins window strings with newlines and encodes as UTF-8 bytes
    for passing to external menu programs like wofi, dmenu, etc.

    Args:
        windows (list): List of formatted window strings.

    Returns:
        bytes: UTF-8 encoded string with windows separated by newlines.

    Examples:
        >>> windows = ['[firefox] Mozilla Firefox', '[terminal] Terminal']
        >>> result = build_wofi_string(windows)
        >>> isinstance(result, bytes)
        True
        >>> b'firefox' in result
        True
        >>> b'terminal' in result
        True
    """
    return ENTER.join(windows).encode("UTF-8")


def show_wofi(windows):
    """
    Display window list in a menu selector and return user selection.

    Executes the configured menu selector (wofi, dmenu, etc.) with the
    provided window list and returns the user's selection.

    Args:
        windows (bytes): UTF-8 encoded window list for the menu.

    Returns:
        bytes: The selected window string, or empty if no selection made.

    Examples:
        >>> # Mock example - actual function spawns external process
        >>> windows_bytes = b'[firefox] Mozilla Firefox\\n[terminal] Terminal\\n'
        >>> # result = show_wofi(windows_bytes)
        >>> # Returns selected line or empty bytes
    """
    process = subprocess.Popen(
        CMD_MENU_SELECTOR,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return process.communicate(input=windows)[0]


def parse_id(windows, parsed_windows, selected):
    """
    Extract the Sway window ID from the user's menu selection.

    Matches the selected window string against the parsed windows list
    to find the corresponding window object and extract its ID.

    Args:
        windows (list): Original list of window dictionaries.
        parsed_windows (list): List of formatted window display strings.
        selected (bytes): Selected window string from the menu.

    Returns:
        str: Sway window ID for focusing the selected window.

    Examples:
        >>> windows = [{'id': 12345, 'app_id': 'firefox', 'name': 'Browser'}]
        >>> parsed = ['[firefox] Browser']
        >>> selected = b'[firefox] Browser\\n'
        >>> window_id = parse_id(windows, parsed, selected)
        >>> window_id
        '12345'
    """
    selected = (selected.decode("UTF-8"))[:-1]  # Remove new line character
    window_index = int(
        parsed_windows.index(selected)
    )  # Get index of selected window in the parsed window array
    return str(windows[window_index].get("id"))  # Get sway window id based on the index


def switch_window(id):
    """
    Switch focus to the window with the specified Sway ID.

    Executes a swaymsg command to focus the window with the given ID.

    Args:
        id (str): Sway window ID to focus.

    Examples:
        >>> # Mock example - actual function calls swaymsg
        >>> switch_window("12345")
        # Executes: swaymsg [con_id=12345] focus
    """
    command = CMD_SWAY_SET_ACTIVE_WINDOW.format(id)

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.communicate()[0]


if __name__ == "__main__":
    """
    Main entry point for the Sway window switcher application.

    Coordinates the workflow:
    1. Get all windows from Sway
    2. Parse them into display format
    3. Show menu for user selection
    4. Switch focus to selected window

    Uses external menu selectors like wofi, dmenu, fuzzel, or rofi.
    """
    parser = ArgumentParser(description="Wofi based window switcher")

    windows = get_windows()

    parsed_windows = parse_windows(windows)

    wofi_string = build_wofi_string(parsed_windows)

    selected = show_wofi(wofi_string)

    try:
        selected_id = parse_id(windows, parsed_windows, selected)
        switch_window(selected_id)
    except ValueError as _:
        # In case there was no selection
        pass
