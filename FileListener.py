



import time, sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import TickScript

class FileChangeHandler(FileSystemEventHandler):

    def __init__(self, filePath):
        self.filePath = filePath

    def on_modified(self, event):
        if event.src_path == self.filePath:
            print(f'event type: {event.event_type}  path: {event.src_path}')

            with open(event.src_path, "r") as file:
                data = file.read()
                print(f'file content type: {data}')
                TickScript.interpreterTest(data)
                print('=============================================')


if __name__ == "__main__":

    p = sys.argv[1]
    print(f'TickScript will be observing {p}')

    eventHandler, observer = FileChangeHandler("./" + p), Observer()
    observer.schedule(eventHandler, path='.', recursive=False)
    observer.start()


    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
