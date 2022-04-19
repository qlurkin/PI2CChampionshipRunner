import glfw
import OpenGL.GL as gl
import imgui
from imgui.integrations.glfw import GlfwRenderer
from state import State, Match
import time
from status import ClientStatus, MatchStatus

FONT_SIZE = 14

from logs import getLogger
from utils import clock

log = getLogger('ui')

textures = []

def createTextureFromPIL(pilImage):
    data = pilImage.tobytes()
    width, height = pilImage.size

    texture = gl.glGenTextures(1)
    textures.append(texture)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, data)

    return texture, width, height

def destroyTextures():
    gl.glDeleteTextures(textures)
    textures.clear()

def impl_glfw_init(title):
    width, height = 1280, 720
    window_name = title

    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(
        int(width), int(height), window_name, None, None
    )
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        exit(1)

    return window

def matchSortKey():
    T = time.time()
    def key(match: Match):
        if match.status == MatchStatus.RUNNING and match.state is not None:
            return - (T - match.start)
        if match.status == MatchStatus.RUNNING:
            return 0
        if match.status == MatchStatus.PENDING:
            return 1
        if match.status == MatchStatus.DONE:
            return 2
    return key

async def ui(gameName, render):
    log.info("UI started")
    imgui.create_context()
    window = impl_glfw_init('{} Runner'.format(gameName.capitalize()))
    impl = GlfwRenderer(window)
    io = imgui.get_io()
    
    #regular = io.fonts.add_font_from_file_ttf('./font/firacode/Fira Code Regular Nerd Font Complete.ttf', FONT_SIZE)
    #bold = io.fonts.add_font_from_file_ttf('./font/firacode/Fira Code Bold Nerd Font Complete.ttf', FONT_SIZE)
    #impl.refresh_font_texture()

    def print_key_value(key, value):
        imgui.text(str(key)+':') 
        imgui.same_line()
        #imgui.push_font(bold)
        imgui.text(str(value))
        #imgui.pop_font()

    tic = clock(60)
    while not glfw.window_should_close(window):
        await tic()
        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()
        #imgui.push_font(regular)

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):

                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", 'Cmd+Q', False, True
                )

                if clicked_quit:
                    exit(1)

                imgui.end_menu()
            imgui.end_main_menu_bar()

        imgui.begin("Clients")
        print_key_value('Count', len(State.clients))
        for client in sorted(State.clients.values(), key=lambda client : -client.points):
            if client.status != ClientStatus.READY:
                imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 0.0, 0.0, 1.0)

            show, _ = imgui.collapsing_header('{}'.format(client.name))
            
            print_key_value('IP', '{}:{}'.format(client.ip, client.port))
            imgui.same_line(spacing=30)
            print_key_value('Points', client.points)
            
            if show:
                print_key_value('Matricules', ', '.join(client.matricules))
                print_key_value('Status', str(client.status).split('.')[1])
                print_key_value('Played', client.matchCount)
                if client.matchCount != 0:
                    print_key_value('Avg Bad Moves', '{0:.2f}'.format(client.badMoves/client.matchCount))

            if client.status != ClientStatus.READY:
                imgui.pop_style_color()
        imgui.end()

        imgui.begin('Matches')
        print_key_value('Remaining', '{}/{}'.format(State.remainingMatches, State.matchCount))
        for match in sorted(State.matches, key=matchSortKey()):
            show, _ = imgui.collapsing_header('{}'.format(match))
            imgui.begin_group()
            if match.state is not None:
                imgui.text('Clients:')
                #imgui.push_font(bold)
                if match.state['current'] == 0:
                    imgui.bullet_text(match.state['players'][0])
                    imgui.push_style_color(imgui.COLOR_TEXT, 0, 0, 0, 0)
                    imgui.bullet()
                    imgui.pop_style_color()
                    imgui.text(match.state['players'][1])
                else:
                    imgui.push_style_color(imgui.COLOR_TEXT, 0, 0, 0, 0)
                    imgui.bullet()
                    imgui.pop_style_color()
                    imgui.text(match.state['players'][0])
                    imgui.bullet_text(match.state['players'][1])
                #imgui.pop_font()
            if match.status == MatchStatus.RUNNING or (match.status == MatchStatus.DONE and show):
                print_key_value('Moves', match.moves)
                if match.start is not None:
                    if match.end is None:
                        print_key_value('Time', '{0:.2f}s'.format(time.time() - match.start))
                    else:
                        print_key_value('Time', '{0:.2f}s'.format(match.end - match.start))
            if match.status == MatchStatus.RUNNING or show:
                print_key_value('Status', str(match.status).split('.')[1])
            if match.status == MatchStatus.DONE:
                print_key_value('Winner', match.winner)
            imgui.end_group()
            if match.state is not None:
                imgui.same_line(position=150)
                imgui.begin_group()
                texture, _, _ = createTextureFromPIL(render(match.state, 300))
                imgui.image(
                    texture_id=texture,
                    width=150,
                    height=150,
                    uv0=(0, 0),
                    uv1=(1, 1),
                    tint_color=(255, 255, 255, 255),
                    border_color=(255, 255, 255, 128),
                )
                imgui.end_group()
                if match.chat is not None:
                    imgui.same_line()
                    imgui.begin_child('chat {}'.format(match), 0, 150, border=True)
                    for message in match.chat.messages:
                        imgui.spacing()
                        imgui.spacing()
                        imgui.text(message.name)
                        #imgui.push_font(bold)
                        imgui.text_wrapped(message.message)
                        #imgui.pop_font()
                        imgui.set_scroll_here()
                    imgui.end_child()
            
            if show:
                pass
        imgui.end()

        #imgui.show_test_window()
        
        #imgui.pop_font()

        gl.glClearColor(.66, .66, .66, 1.)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)
        destroyTextures()
    impl.shutdown()
    glfw.terminate()
