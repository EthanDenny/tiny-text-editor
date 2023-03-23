from blessed import Terminal
import sys
import os

try:
    from colorama import just_fix_windows_console
    just_fix_windows_console()
except Exception:
    pass

# Create an alias to make certain things more clear
def newline():
    print()


TAB_SIZE = 4
LINE_NUM_OFFSET = 6

buffer = ['']

class Cursor:
    x = 0
    y = 0
    ideal_x = 0 # Cursor will move to ideal_x if possible when y changes

cursor = Cursor()

filepath = None

term = Terminal()

ignore = { 'KEY_BEGIN', 'KEY_BTAB', 'KEY_C1', 'KEY_C3', 'KEY_CANCEL',
           'KEY_CATAB', 'KEY_CENTER', 'KEY_CLEAR', 'KEY_CLOSE', 'KEY_COMMAND', 'KEY_COPY',
           'KEY_CREATE', 'KEY_CTAB', 'KEY_DELETE', 'KEY_DL', 'KEY_DOWN', 'KEY_EIC',
           'KEY_END', 'KEY_EOL', 'KEY_EOS', 'KEY_ESCAPE', 'KEY_F0', 'KEY_F1',
           'KEY_F10', 'KEY_F11', 'KEY_F12', 'KEY_F13', 'KEY_F14', 'KEY_F15', 'KEY_F16',
           'KEY_F17', 'KEY_F18', 'KEY_F19', 'KEY_F2', 'KEY_F20', 'KEY_F21', 'KEY_F22',
           'KEY_F23', 'KEY_F3', 'KEY_F4', 'KEY_F5', 'KEY_F6', 'KEY_F7', 'KEY_F8', 'KEY_F9',
           'KEY_FIND', 'KEY_HELP', 'KEY_HOME', 'KEY_IL', 'KEY_INSERT', 'KEY_KP_0',
           'KEY_KP_1', 'KEY_KP_2', 'KEY_KP_3', 'KEY_KP_4', 'KEY_KP_5', 'KEY_KP_6',
           'KEY_KP_7', 'KEY_KP_8', 'KEY_KP_9', 'KEY_KP_ADD', 'KEY_KP_DECIMAL',
           'KEY_KP_DIVIDE', 'KEY_KP_EQUAL', 'KEY_KP_MULTIPLY', 'KEY_KP_SEPARATOR',
           'KEY_KP_SUBTRACT', 'KEY_LL', 'KEY_MARK', 'KEY_MAX', 'KEY_MESSAGE',
           'KEY_MIN', 'KEY_MOUSE', 'KEY_MOVE', 'KEY_NEXT', 'KEY_OPEN', 'KEY_OPTIONS',
           'KEY_PGDOWN', 'KEY_PGUP', 'KEY_PREVIOUS', 'KEY_PRINT', 'KEY_REDO',
           'KEY_REFERENCE', 'KEY_REFRESH', 'KEY_REPLACE', 'KEY_RESET', 'KEY_RESIZE',
           'KEY_RESTART', 'KEY_RESUME', 'KEY_SAVE', 'KEY_SBEG', 'KEY_SCANCEL',
           'KEY_SCOMMAND', 'KEY_SCOPY', 'KEY_SCREATE', 'KEY_SDC', 'KEY_SDL', 'KEY_SDOWN',
           'KEY_SELECT', 'KEY_SEND', 'KEY_SEOL', 'KEY_SEXIT', 'KEY_SFIND', 'KEY_SHELP',
           'KEY_SHOME', 'KEY_SIC', 'KEY_SLEFT', 'KEY_SMESSAGE', 'KEY_SMOVE', 'KEY_SNEXT',
           'KEY_SOPTIONS', 'KEY_SPREVIOUS', 'KEY_SPRINT', 'KEY_SREDO', 'KEY_SREPLACE',
           'KEY_SRESET', 'KEY_SRIGHT', 'KEY_SRSUME', 'KEY_SSAVE', 'KEY_SSUSPEND',
           'KEY_STAB', 'KEY_SUNDO', 'KEY_SUP', 'KEY_SUSPEND', 'KEY_UNDO',
           'KEY_UP', 'KEY_UP_LEFT', 'KEY_UP_RIGHT' }


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
    set_cursor(x=get_end(cursor.y))


def get_bottom():
    return len(buffer)-1


def go_bottom():
    move_cursor(y=get_bottom())


def echo(buffer):
    print(term.plum1(buffer), end='', flush=True)


def delete_next_char():
    saved_buffer = buffer[cursor.y][cursor.x+1:]
    buffer[cursor.y] = buffer[cursor.y][:cursor.x] + buffer[cursor.y][cursor.x+1:]
    with term.location():
        echo(term.clear_eol + saved_buffer[:-1])


def delete_next_newline():
    saved_buffer = buffer.pop(cursor.y + 1)

    old_x = get_end(cursor.y)
    buffer[cursor.y] = buffer[cursor.y][:-1] + saved_buffer
    set_cursor(x=old_x)

    print_lines_after_cursor()


def load():
    global buffer

    if filepath and os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            buffer = []

            for line in f:
                buffer.append(line)
            if buffer[-1][-1] == '\n':
                buffer.append('')


def save():
    if filepath:
        with open(filepath, 'w') as f:
            for i in range(len(buffer)):
                f.write(buffer[i])


def go_ideal_x():
    if cursor.ideal_x <= get_end(cursor.y):
        set_cursor(x=cursor.ideal_x)
    else:
        go_end()


def print_line_num(y):
    echo(term.clear_eol)
    if y < len(buffer):
        print(term.deeppink2(str(y+1).rjust(3) + ' │ '), end='', flush=True)
    else:
        print(term.deeppink2('    │ '), end='', flush=True)

def print_line(y):
    print_line_num(y)
    echo(buffer[y])


def line_before_cursor():
    return buffer[cursor.y][:cursor.x]


def line_after_cursor():
    return buffer[cursor.y][cursor.x:]


def print_lines_after_cursor():
    with term.location(), term.hidden_cursor():
        echo(term.move_x(0))

        for y in range(cursor.y, len(buffer)):
            print_line(y)
        
        newline()
        
        for y in range(len(buffer), term.height - 6):
            print_line_num(y)
            newline()


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


def main():
    global buffer

    load()

    with term.fullscreen(), term.cbreak():
        clear()
        print_header()
        print_lines_after_cursor()

        go_bottom()
        go_end()

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
                        cursor.ideal_x = cursor.x
                elif inp.name == 'KEY_DELETE':
                    if cursor.x < get_end(cursor.y):
                        delete_next_char()
                    elif cursor.y < get_bottom():
                        delete_next_newline()
                elif inp.name == 'KEY_UP':
                    if cursor.y > 0:
                        move_cursor(y=-1)
                        go_ideal_x()
                elif inp.name == 'KEY_DOWN':
                    if cursor.y < get_bottom():
                        move_cursor(y=1)
                        go_ideal_x()
                elif inp.name == 'KEY_LEFT':
                    if cursor.x > 0:
                        move_cursor(x=-1)
                    elif cursor.y > 0:
                        move_cursor(y=-1)
                        go_end()
                elif inp.name == 'KEY_RIGHT':
                    if cursor.x < get_end(cursor.y):
                        move_cursor(x=1)
                    elif cursor.y < get_bottom():
                        move_cursor(y=1)
                        go_home()
                elif inp.name == 'KEY_TAB':
                    out_buffer = ' ' * TAB_SIZE + line_after_cursor()
                    buffer[cursor.y] = line_after_cursor() + out_buffer

                    with term.location():
                        echo(out_buffer)
                    move_cursor(x=TAB_SIZE)
                elif inp.name == 'KEY_ENTER':
                    saved_buffer = line_after_cursor()
                    buffer[cursor.y] = line_before_cursor() + '\n'
                    buffer.insert(cursor.y+1, saved_buffer)

                    print_lines_after_cursor()
                    
                    move_cursor(y=1)
                    go_home()
                elif inp.name == 'KEY_HOME':
                    go_home()
                    cursor.ideal_x = cursor.x
                elif inp.name == 'KEY_END':
                    go_end()
                    cursor.ideal_x = cursor.x
                elif not inp.name in ignore:
                    saved_buffer = line_after_cursor()
                    buffer[cursor.y] = line_before_cursor() + inp + line_after_cursor()

                    with term.location():
                        echo(inp + saved_buffer)
                    move_cursor(x=1)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filepath = sys.argv[1]

    try:
        main()
    except KeyboardInterrupt:
        save()
    except Exception as ex:
        raise ex
