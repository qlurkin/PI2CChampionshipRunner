import glfw
import OpenGL.GL as gl

import imgui
from imgui.integrations.glfw import GlfwRenderer
from testwindow import show_test_window

from PIL import Image, ImageDraw

def drawSomething():
    res = Image.new('RGBA', (100, 100), (50, 50, 50))
    draw = ImageDraw.Draw(res)
    draw.ellipse([5, 5, 95, 95], (255, 0, 0), (255, 255, 255), 3)
    return res

def createTextureFromPIL(pilImage):
    data = pilImage.tobytes()
    width, height = pilImage.size

    texture = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0, gl.GL_RGBA,
                 gl.GL_UNSIGNED_BYTE, data)

    return texture, width, height




def main():
    imgui.create_context()
    window = impl_glfw_init()
    impl = GlfwRenderer(window)

    texture, width, height = createTextureFromPIL(drawSomething())

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):

                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", 'Cmd+Q', False, True
                )

                if clicked_quit:
                    exit(1)

                imgui.end_menu()
            imgui.end_main_menu_bar()


        imgui.begin("Custom window", True)
        imgui.text("Bar")
        imgui.text_ansi("B\033[31marA\033[mnsi ")
        imgui.text_ansi_colored("Eg\033[31mgAn\033[msi ", 0.2, 1., 0.)
        imgui.extra.text_ansi_colored("Eggs", 0.2, 1., 0.)
        imgui.image(
            texture_id=texture,
            width=width,
            height=height,
            uv0=(0, 0),
            uv1=(1, 1),
            tint_color=(255, 255, 255, 255),
            border_color=(255, 255, 255, 128),
        )
        imgui.end()

        show_test_window()
        #imgui.show_test_window()

        gl.glClearColor(1., 1., 1., 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()


def impl_glfw_init():
    width, height = 1280, 720
    window_name = "minimal ImGui/GLFW3 example"

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


if __name__ == "__main__":
    main()