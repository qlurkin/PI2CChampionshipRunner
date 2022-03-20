import glfw
import logging
from utils import clock

log = logging.getLogger('server')

async def ui():
    log.info("UI started")
    glfw.init()
    window = glfw.create_window(640, 480, "Hello World", None, None)
    glfw.make_context_current(window)

    tic = clock(2)
    while not glfw.window_should_close(window):
        #log.info('UI BEFORE TIC')
        await tic()
        #log.info('UI AFTER TIC')
        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()
