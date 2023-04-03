from blessed import Terminal
import sys
import os

try:
    from colorama import just_fix_windows_console
    just_fix_windows_console()
except Exception:
    pass

def load_ignores():
    ignore = set()
    with open('ignore.txt') as f:
        for line in f:
            ignore.add(line)
    return ignore

ignore = load_ignores()

# Create an alias to make certain things more clear
def newline():
    print()


TAB_SIZE = 4
LINE_NUM_OFFSET = 6
HEADER_HEIGHT = 4

buffer = ['']

class Cursor:
    x = 0
    y = 0
    ideal_x = 0 # Cursor will move to ideal_x if possible when y changes

cursor = Cursor()

filepath = None

term = Terminal()

ignore = []
with open('ignore.txt') as f:
    for line in f:
        ignore.append(line)

screen_offset = 0


def move_internal_cursor(x=0, y=0):
    cursor.x += x
    cursor.y += y

    if x != 0: cursor.ideal_x = cursor.x


def move_terminal_cursor(x=0, y=0):
    if x < 0: echo(term.move_left(-x))
    if x > 0: echo(term.move_right(x))
    if y < 0: echo(term.move_up(-y))
    if y > 0: echo(term.move_down(y))


def move_cursor(x=0, y=0):
    move_internal_cursor(x, y)
    move_terminal_cursor(x, y)


def set_internal_cursor(x=None, y=None):
    if x != None: cursor.x = x
    if y != None: cursor.y = y


def set_terminal_cursor(x=None, y=None):
    if x != None: echo(term.move_x(x + LINE_NUM_OFFSET))
    if y != None: echo(term.move_y(y))


def set_cursor(x=None, y=None):
    set_internal_cursor(x, y)
    set_terminal_cursor(x, y)


def go_home():
    set_cursor(x=0)


def get_end(line):
    if len(buffer[line]) > 0 and buffer[line][-1] == '\n':
        return len(buffer[line]) - 1
    else:
        return len(buffer[line])


def go_end():
    set_cursor(x=get_end(cursor.y + screen_offset))


def get_bottom():
    return term.height - HEADER_HEIGHT - 2


def echo(buffer):
    print(term.plum1(buffer), end='', flush=True)


def delete_next_char():
    saved_buffer = buffer[cursor.y + screen_offset][cursor.x+1:]
    buffer[cursor.y + screen_offset] = buffer[cursor.y + screen_offset][:cursor.x] + buffer[cursor.y + screen_offset][cursor.x+1:]
    with term.location():
        echo(term.clear_eol + saved_buffer[:-1])


def delete_next_newline():
    saved_buffer = buffer.pop(cursor.y + screen_offset + 1)

    old_x = get_end(cursor.y + screen_offset)
    buffer[cursor.y + screen_offset] = buffer[cursor.y + screen_offset][:-1] + saved_buffer
    set_cursor(x=old_x)

    print_lines_after_cursor()


def load():
    global buffer

    if filepath and os.path.isfile(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            buffer = []

            for line in f:
                buffer.append(line)
            if buffer[-1][-1] == '\n':
                buffer.append('')


def save():
    if filepath:
        with open(filepath, 'w', encoding='utf-8') as f:
            for i in range(len(buffer)):
                f.write(buffer[i])


def go_ideal_x():
    if cursor.ideal_x <= get_end(cursor.y + screen_offset):
        set_cursor(x=cursor.ideal_x)
    else:
        go_end()


def print_line(y):
    echo(term.clear_eol)
    if y < len(buffer):
        print(term.deeppink2(str(y+1).rjust(3) + ' │ '), end='', flush=True)
        echo(buffer[y])
    else:
        if y == len(buffer): print('\r')
        print(term.deeppink2('    │\n'), end='', flush=True)


def line_before_cursor():
    return buffer[cursor.y + screen_offset][:cursor.x]


def line_after_cursor():
    return buffer[cursor.y + screen_offset][cursor.x:]


def print_slice(terminal_line, buffer_line_start, buffer_line_end):
    num_of_lines = min(buffer_line_end - buffer_line_start, term.height - terminal_line - 1)

    with term.location(), term.hidden_cursor():
        echo(term.move_x(0))
        echo(term.move_y(terminal_line))

        for i in range(num_of_lines):
            print_line(buffer_line_start + i)


def print_lines_after_cursor():
    print_slice(cursor.y + HEADER_HEIGHT, cursor.y, term.height)


def clear():
    echo(term.home + term.clear)


def print_header():
    print(term.bold_deeppink('╔' + '═'*(term.width-2) + '╗'))

    if filepath:
        print(term.bold_deeppink(f'║ editing: {filepath}' + ' '*(term.width-len(filepath)-12) + '║'))
    else:
        print(term.bold_deeppink(f'║ tiny text' + ' '*(term.width-12) + '║'))

    print(term.bold_deeppink('╚' + '═══╤' + '═'*(term.width-LINE_NUM_OFFSET) + '╝'))
    print(term.deeppink2('    │'))


def print_full_screen():
    print_slice(HEADER_HEIGHT, screen_offset, len(buffer))


def move_offset_up():
    global screen_offset
    screen_offset = max(screen_offset - 1, 0)
    print_full_screen()


def move_offset_down():
    global screen_offset
    screen_offset = min(screen_offset + 1, len(buffer) - term.height + 5)
    print_full_screen()


def put_text(text):
    saved_buffer = line_after_cursor()
    buffer[cursor.y + screen_offset] = line_before_cursor() + text + line_after_cursor()

    with term.location():
        echo(text + saved_buffer)
    
    move_cursor(x=len(text))


def update_ideal_x():
    cursor.ideal_x = cursor.x


def main():
    global buffer
    global screen_offset

    load()

    with term.fullscreen(), term.cbreak():
        clear()
        print_header()
        print_lines_after_cursor()

        set_terminal_cursor(x=0, y=HEADER_HEIGHT)

        while True:
            inp = term.inkey()

            with term.hidden_cursor():
                if inp.name == 'KEY_BACKSPACE':
                    if cursor.x > 0:
                        move_cursor(x=-1)
                        delete_next_char()
                    elif cursor.y > 0:
                        move_cursor(y=-1)
                        delete_next_newline()
                        update_ideal_x()
                elif inp.name == 'KEY_DELETE':
                    if cursor.x < get_end(cursor.y + screen_offset):
                        delete_next_char()
                    elif cursor.y < get_bottom():
                        delete_next_newline()
                elif inp.name == 'KEY_UP':
                    if cursor.y > 0:
                        move_cursor(y=-1)
                        go_ideal_x()
                    else:
                        move_offset_up()
                    go_ideal_x()
                elif inp.name == 'KEY_DOWN':
                    if cursor.y < get_bottom():
                        move_cursor(y=1)
                    else:
                        move_offset_down()
                    go_ideal_x()
                elif inp.name == 'KEY_LEFT':
                    if cursor.x > 0:
                        move_cursor(x=-1)
                    elif cursor.y > 0:
                        move_cursor(y=-1)
                        go_end()
                elif inp.name == 'KEY_RIGHT':
                    if cursor.x < get_end(cursor.y + screen_offset):
                        move_cursor(x=1)
                    elif cursor.y < get_bottom():
                        move_cursor(y=1)
                        go_home()
                elif inp.name == 'KEY_TAB':
                    put_text(' ' * TAB_SIZE)
                elif inp.name == 'KEY_ENTER':
                    saved_buffer = line_after_cursor()
                    buffer[cursor.y + screen_offset] = line_before_cursor() + '\n'
                    buffer.insert(cursor.y + screen_offset + 1, saved_buffer)

                    print_lines_after_cursor()
                    
                    move_cursor(y=1)
                    go_home()
                elif inp.name == 'KEY_HOME':
                    go_home()
                    update_ideal_x()
                elif inp.name == 'KEY_END':
                    go_end()
                    update_ideal_x()
                elif not inp.name in ignore:
                    put_text(inp)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filepath = sys.argv[1]

    try:
        main()
    except KeyboardInterrupt:
        save()
    except Exception as ex:
        raise ex
