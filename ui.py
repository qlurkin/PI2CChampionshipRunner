import time

import glfw
import imgui
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer

from logs import getLogger
from state import Match, State
from status import ClientStatus, MatchStatus
from utils import clock

FONT_SIZE = 14

log = getLogger("ui")

textures = []


def createTextureFromPIL(pilImage):
    data = pilImage.tobytes()
    width, height = pilImage.size

    texture = gl.glGenTextures(1)
    textures.append(texture)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexImage2D(
        gl.GL_TEXTURE_2D,
        0,
        gl.GL_RGBA,
        width,
        height,
        0,
        gl.GL_RGBA,
        gl.GL_UNSIGNED_BYTE,
        data,
    )

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
    window = glfw.create_window(int(width), int(height), window_name, None, None)
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
            assert match.start is not None
            return -(T - match.start)
        if match.status == MatchStatus.RUNNING:
            return 0.0
        if match.status == MatchStatus.PENDING:
            return 1.0
        if match.status == MatchStatus.DONE:
            return 2.0
        return float("Inf")

    return key


async def ui(gameName, render):
    log.info("UI started")
    imgui.core.create_context()
    window = impl_glfw_init("{} Runner".format(gameName.capitalize()))
    impl = GlfwRenderer(window)
    # io = imgui.get_io()  # pyright: ignore

    def print_key_value(key, value):
        imgui.core.push_style_color(imgui.COLOR_TEXT, 0.8, 0.8, 0.8)
        imgui.core.text(str(key) + ":")
        imgui.core.pop_style_color()
        imgui.core.same_line()
        imgui.core.text(str(value))

    tic = clock(60)
    while not glfw.window_should_close(window):
        await tic()
        glfw.poll_events()
        impl.process_inputs()

        imgui.core.new_frame()

        if imgui.core.begin_main_menu_bar():
            if imgui.core.begin_menu("File", True):

                clicked_quit, _ = imgui.core.menu_item("Quit", "Cmd+Q", False, True)

                if clicked_quit:
                    exit(1)

                imgui.core.end_menu()
            imgui.core.end_main_menu_bar()

        imgui.core.begin("Clients")
        print_key_value("Count", len(State.clients))
        for client in sorted(
            State.clients.values(), key=lambda client: -State.getPoints(client)
        ):
            imgui.core.push_id(str(client.matricules))
            if client.status != ClientStatus.READY:
                imgui.core.push_style_color(imgui.COLOR_TEXT, 1.0, 0.0, 0.0, 1.0)

            show, _ = imgui.core.collapsing_header("{}".format(client.name))

            print_key_value("IP", "{}:{}".format(client.ip, client.port))
            imgui.core.same_line(spacing=30)
            print_key_value("Points", State.getPoints(client))

            if show:
                print_key_value("Matricules", ", ".join(client.matricules))
                print_key_value("Status", str(client.status).split(".")[1])
                clientMatchCount = State.getMatchCount(client)
                print_key_value("Played", clientMatchCount)
                if clientMatchCount != 0:
                    print_key_value(
                        "Avg Bad Moves",
                        "{0:.2f}".format(State.getBadMoves(client) / clientMatchCount),
                    )
                if imgui.core.button("Unsubscribe"):
                    await State.removeClient(client.matricules)

            if client.status != ClientStatus.READY:
                imgui.core.pop_style_color()
            imgui.core.pop_id()
        imgui.core.end()

        imgui.core.begin("Matches")
        print_key_value(
            "Remaining",
            "{}/{} (running: {})".format(
                State.remainingMatches, State.matchCount, State.runningMatches
            ),
        )
        for match in sorted(State.matches, key=matchSortKey()):
            imgui.core.push_id(str(match))
            show, _ = imgui.core.collapsing_header("{}".format(match))
            imgui.core.begin_group()
            if match.state is not None:
                imgui.core.text("Clients:")
                if match.state["current"] == 0:
                    imgui.core.bullet_text(match.state["players"][0])
                    imgui.core.push_style_color(imgui.COLOR_TEXT, 0, 0, 0, 0)
                    imgui.core.bullet()
                    imgui.core.pop_style_color()
                    imgui.core.text(match.state["players"][1])
                else:
                    imgui.core.push_style_color(imgui.COLOR_TEXT, 0, 0, 0, 0)
                    imgui.core.bullet()
                    imgui.core.pop_style_color()
                    imgui.core.text(match.state["players"][0])
                    imgui.core.bullet_text(match.state["players"][1])
            if match.status == MatchStatus.RUNNING or (
                match.status == MatchStatus.DONE and show
            ):
                print_key_value("Moves", match.moves)
                if match.start is not None:
                    if match.end is None:
                        print_key_value(
                            "Time", "{0:.2f}s".format(time.time() - match.start)
                        )
                    else:
                        print_key_value(
                            "Time", "{0:.2f}s".format(match.end - match.start)
                        )
            if match.status == MatchStatus.RUNNING or show:
                print_key_value("Status", str(match.status).split(".")[1])
            if match.status == MatchStatus.DONE:
                print_key_value("Winner", match.winner)
            if match.status == MatchStatus.RUNNING or show:
                if imgui.core.button("Reset"):
                    await match.reset()
            imgui.core.end_group()
            if match.state is not None:
                imgui.core.same_line(position=150)
                imgui.core.begin_group()
                texture, _, _ = createTextureFromPIL(render(match.state, 300))
                imgui.core.image(
                    texture_id=texture,
                    width=150,
                    height=150,
                    uv0=(0, 0),
                    uv1=(1, 1),
                    tint_color=(255, 255, 255, 255),
                    border_color=(255, 255, 255, 128),
                )
                imgui.core.end_group()
                if match.chat is not None:
                    imgui.core.same_line()
                    imgui.core.begin_child("chat {}".format(match), 0, 150, border=True)
                    for message in match.chat.messages:
                        imgui.core.spacing()
                        imgui.core.spacing()
                        imgui.core.text(message.name)
                        imgui.core.text_wrapped(message.message)
                        imgui.core.set_scroll_here_y()
                    imgui.core.end_child()
            imgui.core.pop_id()
        imgui.core.end()

        gl.glClearColor(0.66, 0.66, 0.66, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.core.render()
        impl.render(imgui.core.get_draw_data())
        glfw.swap_buffers(window)
        destroyTextures()
    impl.shutdown()
    glfw.terminate()
