"""
Factory for creating request handlers.
"""
from yaha.log.log import LogHelper


class HandlerFactory:
    """
    Factory for creating request handlers
    """
    _handlers = {}
    _app_handlers = {}
    _context = {}

    @classmethod
    def register_handler(
            cls,
            request_type,
            app_handler_cls,
            request_handler_cls,
            request_context=None,
            response_context=None):
        """
        注册处理程序。

        Args:
            request_type: 请求类型。
            app_handler_cls: 应用程序处理程序类。
            request_handler_cls: 请求处理程序类。

        Returns:
            None
        """
        LogHelper.info(f"Register handler for request_type: {request_type}")
        cls._handlers[request_type] = request_handler_cls
        cls._app_handlers[request_type] = app_handler_cls()
        cls._context[request_type] = {"request": request_context, "response": response_context}

    @classmethod
    def get_handlers(cls):
        """
        获取所有注册的处理类
        :return:
        """
        return cls._handlers

    @classmethod
    def get_handler(cls, request_type):
        """
        根据请求类型获取对应的处理类

        Args:
            request_type (str): 请求类型

        Returns:
            Tuple[Any, Any]: 返回一个元组，第一个元素为处理类的实例，第二个元素为处理类本身

        Raises:
            ValueError: 当没有为指定类型注册处理类时，抛出该异常
        """
        app_handler = cls._app_handlers.get(request_type)
        request_handler_cls = cls._handlers.get(request_type)
        if not request_handler_cls or not app_handler:
            LogHelper.error(f"No handler registered for request_type: {request_type}")
            raise ValueError(f"No handler registered for request_type: {request_type}")
        return app_handler, request_handler_cls(app_handler)
