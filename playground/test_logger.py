from linovelib2epub.logger import Logger

if __name__ == '__main__':
    logger = Logger(logger_name="my-log",log_dir="./logs/").get_logger()
    logger.info("Logging set up.")
    logger.error("Logging error.")

    def division(a, b):
        logger.debug(f"Dividing {a} by {b}.")
        try:
            return a / b
        except ZeroDivisionError:
            logger.exception("Oh noes!")


    division(5, 0)