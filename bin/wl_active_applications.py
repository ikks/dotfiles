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
    parsed_windows = []
    for window in windows:
        parsed_windows.append(
            "[{}] {}".format(window.get("app_id"), window.get("name"))
        )
    return parsed_windows


def build_wofi_string(windows):
    return ENTER.join(windows).encode("UTF-8")


def show_wofi(windows):
    process = subprocess.Popen(
        CMD_MENU_SELECTOR,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return process.communicate(input=windows)[0]


def parse_id(windows, parsed_windows, selected):
    selected = (selected.decode("UTF-8"))[:-1]  # Remove new line character
    window_index = int(
        parsed_windows.index(selected)
    )  # Get index of selected window in the parsed window array
    return str(windows[window_index].get("id"))  # Get sway window id based on the index


def switch_window(id):
    command = CMD_SWAY_SET_ACTIVE_WINDOW.format(id)

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.communicate()[0]


if __name__ == "__main__":
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
