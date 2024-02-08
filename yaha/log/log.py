"""
Logging utilities.
"""
import os
import time
import random

import psutil
import GPUtil
import logging
import threading

from logging.handlers import TimedRotatingFileHandler


class CustomLogRecord(logging.LogRecord):
    """
    Custom log record class.
    """

    def __init__(self, *args, **kwargs):
        """
        初始化函数，用于创建CustomLogRecord对象。

        Args:
            *args: 可变位置参数，传递给父类CustomLogRecord的__init__函数。
            **kwargs: 关键字参数，传递给父类CustomLogRecord的__init__函数。

        Returns:
            None

        """
        super(CustomLogRecord, self).__init__(*args, **kwargs)
        self.pid = os.getpid()


class NoErrorFilter(logging.Filter):
    """
    Custom log 日志过滤器
    """

    def filter(self, record):
        """

        Args:
            record:

        Returns:

        """
        # 返回False表示过滤掉该日志记录
        return record.levelno < logging.ERROR


class CustomFormatter(logging.Formatter):
    """
    Custom log formatter class.
    """

    def format(self, record):
        """
        格式化日志记录，返回格式化后的字符串。

        Args:
            record (logging.LogRecord): 日志记录对象。

        Returns:
            str: 格式化后的字符串。
        """
        if 'logid' not in record.__dict__:
            record.__dict__['logid'] = 'default'
        return super(CustomFormatter, self).format(record)


class LogHelper:
    """
    Helper class to log messages.
    """
    _logger = None
    _thread_local = threading.local()
    _is_logger_setup = False

    @classmethod
    def file_handler(cls, filename):
        """
        正常文件流
        Args:
            filename:

        Returns:

        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        handler = logging.handlers.TimedRotatingFileHandler(
            filename, when="H", interval=1, backupCount=24 * 7)
        handler.suffix = "%Y%m%d%H"

        return handler

    @classmethod
    def file_warn_handler(cls, filename):
        """
        错误文件流
        Args:
            filename:

        Returns:

        """
        # 如果提供了警告日志文件，则为警告日志设置单独的处理器
        warn_log_file = filename + '.wf'
        warn_handler = logging.FileHandler(warn_log_file)

        return warn_handler

    @classmethod
    def stream_handler(cls):
        """
        控制台输出流
        Returns:

        """
        handler = logging.StreamHandler()
        return handler

    @classmethod
    def setup_logger(cls, log_file=None, log_level=logging.DEBUG):
        """
        设置日志记录器。

        Args:
            log_file (str): 日志文件路径。
            log_level (int, optional): 日志级别。默认为logging.INFO。

        Returns:
            None
        """

        if cls._is_logger_setup:
            # 如果已经设置了日志配置，先清除现有的handlers
            cls._logger.handlers.clear()

        logging.setLogRecordFactory(CustomLogRecord)
        cls._logger = logging.getLogger()
        formatter = CustomFormatter(
            '[%(asctime)s] [pid:%(process)d] [level:%(levelname)s] [logid:%(logid)s] %(message)s')

        # 根据是否提供了log_file参数来添加不同的handler
        if log_file:
            handler = cls.file_handler(filename=log_file)
            handler.setFormatter(formatter)
            handler.addFilter(NoErrorFilter())
            cls._logger.addHandler(handler)

            # 添加警告日志文件处理器
            warn_handler = cls.file_warn_handler(filename=log_file)
            warn_handler.setFormatter(formatter)
            warn_handler.setLevel(logging.WARNING)
            cls._logger.addHandler(warn_handler)
        else:
            # 没有提供log_file时，添加控制台日志处理器
            handler = cls.stream_handler()
            handler.setFormatter(formatter)
            cls._logger.addHandler(handler)

        cls._logger.setLevel(log_level)
        cls._logger.propagate = False
        cls._is_logger_setup = True  # 标记_logger已经被设置

    @classmethod
    def _get_system_usage(cls):
        """
        获取系统使用情况

        Args:
            无

        Returns:
            tuple: 包含三个值的元组，分别为cpu使用率，内存使用率和GPU使用率

        """
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        gpus = GPUtil.getGPUs()
        gpu_usage = round(gpus[0].load * 100, 2) if gpus else 0
        return cpu_usage, memory_usage, gpu_usage

    @classmethod
    def set_logid(cls, logid):
        """
        设置当前线程的日志ID。

        Args:
            logid (str): 当前线程的日志ID。

        Returns:
            None
        """
        cls._thread_local.logid = logid

    @classmethod
    def _log(cls, level, message):
        """
        记录日志信息。

        Args:
            level (str): 日志级别，可选值为'debug', 'info', 'warning', 'error', 'critical'。
            message (str): 日志信息。

        Returns:
            None
        """
        if cls._logger:
            cpu, mem, gpu = cls._get_system_usage()
            logid = getattr(cls._thread_local, 'logid', 'default')
            log_message = f'[CPU: {cpu}] [Memory: {mem}] [GPU: {gpu}] {message} '
            cls._logger.log(level, log_message, extra={'logid': logid})

    @classmethod
    def info(cls, message):
        """
        将信息级别的日志写入日志文件。

        Args:
            message: 需要记录的信息，类型为str。

        Returns:
            无返回值。

        """
        cls._log(logging.INFO, message)

    @classmethod
    def warning(cls, message):
        """
        将信息级别的日志写入日志文件。

        Args:
            message: 需要记录的信息，类型为str。

        Returns:
            无返回值。

        """
        cls._log(logging.WARNING, message)

    @classmethod
    def debug(cls, message):
        """
        将信息级别的日志写入日志文件。

        Args:
            message: 需要记录的信息，类型为str。

        Returns:
            无返回值。

        """
        cls._log(logging.DEBUG, message)

    @classmethod
    def error(cls, message):
        """
        将信息级别的日志写入日志文件。

        Args:
            message: 需要记录的信息，类型为str。

        Returns:
            无返回值。

        """
        cls._log(logging.ERROR, message)

    @classmethod
    def fatal(cls, message):
        """
        将信息级别的日志写入日志文件。

        Args:
            message: 需要记录的信息，类型为str。

        Returns:
            无返回值。

        """
        cls._log(logging.FATAL, message)

    @classmethod
    def get_logid(cls):
        """
        获取当前线程的日志ID。
        Args:
            无
        Returns:
            str: 当前线程的日志ID。
        """
        logid = str(int(time.time() * 1000)) + str(random.randint(0, 9999))
        return getattr(cls._thread_local, 'logid', logid)


LogHelper.setup_logger()
