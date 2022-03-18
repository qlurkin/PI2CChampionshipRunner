from gc import callbacks
import threading as th
import glfw

def ui():
    print("UI started")
    glfw.init()
    window = glfw.create_window(640, 480, "Hello World", None, None)
    glfw.make_context_current(window)

    while not glfw.window_should_close(window):
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

def championship():
    print('Championship Task Started')
    def turn():
        pass
    stop = RepeatInThread(turn).onStop(lambda : print('Championship Task Stopped'))
    return stop

def inscription():
    print('Inscription Task Started')
    def turn():
        pass
    stop = RepeatInThread(turn).onStop(lambda : print('Inscription Task Stopped'))
    return stop

class Obj:
    def __init__(self, **kwargs):
        self.__call__(**kwargs)

    def __getitem__(self, key):
        getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __call__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self


class RepeatInThread:
    def __init__(self, fun):
        self.__callbacks = []
        self.__running = True
        def loop():
            while self.__running:
                fun()

        self.__thread = th.Thread(target=loop, daemon=False)
        self.__thread.start()

    def onStop(self, fun):
        self.__callbacks.append(fun)
        return self

    def stop(self):
        self.__running = False
        self.__thread.join()
        for fun in self.__callbacks:
            fun()

class Promise:
    def __init__(self, fun):
        self.__PENDING = 1
        self.__RESOLVED = 2
        self.__REJECTED = 3
        self.__successCallbacks = []
        self.__errorCallbacks = []
        self.__state = self.__PENDING
        self.__value = None
        self.__error = None

        def resolve(value=None):
            self.__value = value
            self.__state = self.__RESOLVED
            for fun in self.__successCallbacks:
                fun(value)

        def reject(error=None):
            self.__error = error
            self.__state = self.__REJECTED
            for fun in self.__errorCallbacks:
                fun(error)

        self.__thread = th.Thread(target=fun, args=(resolve, reject), daemon=True)
        self.__thread.start()

    def then(self, fun):
        if self.__state == self.__PENDING:
            self.__successCallbacks.append(fun)
        elif self.__state == self.__RESOLVED:
            fun(self.__value)

    def catch(self, fun):
        if self.__state == self.__PENDING:
            self.__errorCallbacks.append(fun)
        elif self.__state == self.__REJECTED:
            fun(self.__error)

def repeatInThread(fun):
    callbacks = []
    running = True

    def loop():
        while running:
            fun()

    thread = th.Thread(target=loop, daemon=False)
    thread.start()

    that = Obj()

    def onStop(fun):
        callbacks.append(fun)
        return that
    
    def stop():
        nonlocal running
        running = False
        thread.join()
        for fun in callbacks:
            fun()

    return that(stop=stop, onStop=onStop)


def main():
    stopInscription = inscription()
    stopChampionship = championship()
    ui()
    stopInscription.stop()
    stopChampionship.stop()

if __name__ == '__main__':
    main()