from blessed import Terminal
import sys
from colorama import just_fix_windows_console

just_fix_windows_console()

TAB_SIZE = 4

cursor_x = 1
cursor_y = 1

term = Terminal()

def move_internal_cursor(x=0, y=0):
    global cursor_x
    global cursor_y
    cursor_x += x
    cursor_y += y

def move_terminal_cursor(x=0, y=0):
    if x < 0: echo(term.move_left(-x))
    if x > 0: echo(term.move_right(x))
    if y < 0: echo(term.move_up(-y))
    if y > 0: echo(term.move_down(y))

def move_cursor(x=0, y=0):
    move_internal_cursor(x, y)
    move_terminal_cursor(x, y)

def set_internal_cursor(x=None, y=None):
    global cursor_x
    global cursor_y
    if x != None: cursor_x = x
    if y != None: cursor_y = y

def set_terminal_cursor(x=None, y=None):
    if x != None: echo(term.move_x(x))
    if y != None: echo(term.move_y(y))

def set_cursor(x=None, y=None):
    set_internal_cursor(x, y)
    set_terminal_cursor(x, y)

def echo(buffer):
    print(term.plum1(buffer), end='', flush=True)

term.number_of_colors = 1 << 24

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

def main():
    buffer = ''      

    with term.fullscreen(), term.cbreak():
        echo(term.home + term.clear)
        print(term.bold_deeppink('╔' + '═'*(term.width-2) + '╗'))
        print(term.bold_deeppink('║ welcome to tiny text' + ' '*(term.width-23) + '║'))
        print(term.bold_deeppink('╚' + '═'*(term.width-2) + '╝\n'))

        while True:
            inp = term.inkey()

            if inp.name in ignore: continue

            match inp.name:
                case 'KEY_BACKSPACE':
                    if cursor_x > 1:
                        move_cursor(x=-1)
                        saved_buffer = buffer[cursor_x:]
                        buffer = buffer[:cursor_x-1] + buffer[cursor_x:]
                        echo(term.clear_eol + saved_buffer)
                        move_terminal_cursor(x=-len(saved_buffer))
                case 'KEY_DELETE':
                    saved_buffer = buffer[cursor_x:]
                    buffer = buffer[:cursor_x-1] + buffer[cursor_x:]
                    echo(term.clear_eol + saved_buffer)
                    move_terminal_cursor(x=-len(saved_buffer))
                case 'KEY_LEFT':
                    if cursor_x > 1:
                        move_cursor(x=-1)
                case 'KEY_RIGHT':
                    if cursor_x <= len(buffer):
                        move_cursor(x=1)
                case 'KEY_TAB':
                    with term.location():
                        out_buffer = ' ' * TAB_SIZE + buffer[cursor_x-1:]
                        buffer = buffer[:cursor_x-1] + out_buffer
                        echo(out_buffer)
                    move_cursor(x=TAB_SIZE)
                case 'KEY_ENTER':
                    with term.location():
                        saved_buffer = buffer[cursor_x-1:]
                        buffer = buffer[:cursor_x-1] + '\n' + buffer[cursor_x-1:]
                        echo('\n' + saved_buffer)
                    move_cursor(y=1)
                    set_cursor(x=0)
                case _:
                    with term.location():
                        saved_buffer = buffer[cursor_x-1:]
                        buffer = buffer[:cursor_x-1] + inp + buffer[cursor_x-1:]
                        echo(inp + saved_buffer)
                    move_cursor(x=1)

            """
            with term.location():
                echo(f'\n\n{cursor_x:2d}')
                echo(f'\n{term.clear_eol}{buffer}')
            """

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        raise ex