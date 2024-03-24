from linovelib2epub import Linovelib2Epub
import threading
import concurrent.futures


def task(book):
    try:
        linovelib_epub = Linovelib2Epub(book_id=book, divide_volume=True)
        linovelib_epub.run()
        return f"{book},done"
    except Exception as e:
        return f"{book},error"


def write_to_file(lock, filename, data):
    with lock:
        with open(filename, "a") as f:
            f.write(data + "\n")


def main():
    filename = "task_results.txt"
    lock = threading.Lock()
    open(filename, "w").close()

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(task, n) for n in range(4055)]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            write_to_file(lock, filename, result)


if __name__ == "__main__":
    # main()
    linovelib_epub = Linovelib2Epub(book_id=1145, divide_volume=True)
    linovelib_epub.run()
