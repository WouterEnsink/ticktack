
import time, sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread


class FileChangeListener(FileSystemEventHandler):
    def __init__(self, filePath):
        self.thread = Thread(target=self.run)
        self.filePath = filePath


    def startListening(self):
        self.shouldRun = True
        self.thread.start()

    def run(self):
        observer = Observer()
        observer.schedule(self, path='.', recursive=False)
        observer.start()

        while self.shouldRun:
            time.sleep(1)

        observer.join()


    def stopListening(self):
        self.shouldRun = False
        self.thread.join()


    def on_modified(self, event):
        if event.src_path == self.filePath:
            self.fileChanged(self.filePath)


    # meant to be overridden by subclass
    def fileChanged(self, newFileData):
        pass



if __name__ == "__main__":

    p = sys.argv[1]
    print(f'TickScript will be observing {p}')

    eventHandler, observer = FileChangeListener("./" + p), Observer()
    observer.schedule(eventHandler, path='.', recursive=False)
    observer.start()


    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
