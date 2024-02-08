"""
This module provides the web service for Tide.
"""
import os
import time
import json
from abc import ABC, abstractmethod
import uvicorn

from fastapi import FastAPI, Request, HTTPException

from yaha.log.log import LogHelper
from yaha.web_api.factory import HandlerFactory
from yaha.web_api.request_process import RequestProcess


class ConfigHandler(ABC):
    """
    Abstract class for config handler.
    """

    def __init__(self):
        """
        初始化函数，用于初始化配置。

        Args:
            无参数。

        Returns:
            无返回值。

        Raises:
            Exception: 初始化失败时抛出异常。
        """
        try:
            st = time.time()
            self.bootstrap()
            self.initialize()
            et = time.time()
            LogHelper.info(f"Initialize config success, cost {et - st}s")
        except Exception as e:
            LogHelper.error(f"Failed to initialize config: {e}")
            raise

    @abstractmethod
    def initialize(self):
        """
        初始化方法，需要在子类中实现。

        Args:
            无参数。

        Returns:
            无返回值。

        """

    def bootstrap(self):
        """
        启动web服务

        Args:
            无

        Returns:
            无
        """
        log_file = os.environ.get("LOG_FILE", "logs/web_service.py.log")
        # if not os.path.exists(log_file):
        #     LogHelper.error(f"Log file {log_file} does not exist.")
        #     raise Exception(f"Log file {log_file} does not exist.")
        LogHelper.setup_logger(log_file)
        LogHelper.info("Starting web service")


class RequestHandler(ABC):
    """
    Abstract class for request handler.
    """

    def __init__(self, app_handler):
        """
        初始化函数，将传入的app_handler赋值给self.app_config

        Args:
            app_handler (object): 应用程序配置对象

        Returns:
            None
        """
        self.app_config = app_handler

    @abstractmethod
    def pre_process(self, request_body):
        """
        前处理函数，将传入的request_body进行预处理，并返回预处理后的结果。

        Args:
            request_body (dict): 请求体

        Returns:
            None
        """

    @abstractmethod
    def run(self, processed_input):
        """
        推理函数，将传入的processed_input进行推理，并返回推理结果。
        Args:
            processed_input:

        Returns:

        """

    @abstractmethod
    def post_process(self, inference_result):
        """
        后处理函数，将传入的inference_result进行后处理，并返回后处理后的结果。
        Args:
            inference_result:

        Returns:

        """


def create_route_handler(handler_type):
    """
    创建路由处理函数。
    Args:
        handler_type:

    Returns:

    """

    async def route_handler(request: Request):
        """
        路由处理函数。
        Args:
            request:

        Returns:

        """
        handler = RequestProcess(request, handler_type)
        return await handler.process_request()


    return route_handler


async def parse_request(request: Request):
    """
    解析请求体并返回 JSON 格式的数据。

    Args:
        request (Request): 请求对象，包含请求体数据。

    Returns:
        dict: 解析后的 JSON 格式数据。

    Raises:
        HTTPException: 如果请求体不是有效的 JSON 格式数据，则抛出 HTTPException 异常，异常的 status_code 为 400，detail 为 "Invalid JSON data"。
    """
    if request is None:
        LogHelper.warning("Request is None")
        return ""
    try:
        request_body = await request.json()
    except json.JSONDecodeError as e:
        LogHelper.error("Invalid JSON data")
        raise HTTPException(status_code=400, detail="Invalid JSON data") from e
    return request_body


def start_app(host="0.0.0.0", port=8000):
    """
    启动 FastAPI 服务器

    Args:
        host (str, optional): 服务器监听的 IP 地址，默认为 "0.0.0.0"。
        port (int, optional): 服务器监听的端口号，默认为 8000。

    Returns:
        FastAPI: FastAPI 应用实例。
    """
    app = FastAPI()

    handlers = HandlerFactory.get_handlers()
    for handler_type, handler_cls in handlers.items():
        route_handler = create_route_handler(handler_type)
        LogHelper.debug(f"Register route: {handler_type}, handler_cls: {handler_cls}")
        app.post(f"{handler_type}")(route_handler)

    uvicorn.run(app, host=host, port=port)
    return app
