import glfw
from logs import getLogger
from utils import clock

log = getLogger('ui')

async def ui():
    log.info("UI started")
    glfw.init()
    window = glfw.create_window(640, 480, "Hello World", None, None)
    glfw.make_context_current(window)

    tic = clock(2)
    while not glfw.window_should_close(window):
        await tic()
        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()
