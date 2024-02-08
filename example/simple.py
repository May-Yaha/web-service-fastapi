"""
Simple example for chatbot.
"""
from pydantic import BaseModel

from yaha.web_api.web_service import ConfigHandler, RequestHandler, start_app
from yaha.web_api.factory import HandlerFactory


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


class ChatAppHandler(ConfigHandler):
    def initialize(self):
        """
        初始化方法，设置应用程序名称为"test"。

        Args:
            无参数。

        Returns:
            无返回值。
        """
        self.app_name = "test"


class ChatHandler(RequestHandler):
    def pre_process(self, request_body):
        """
        对请求体进行预处理。

        Args:
            request_body (dict): 请求体，包含聊天信息。

        Returns:
            dict: 预处理后的请求体。
        """
        print("model_name: ", self.app_config.app_name)
        # 实现特定于聊天的预处理
        return request_body

    def run(self, processed_input):
        """
        运行聊天逻辑

        Args:
            processed_input (dict): 经过处理的输入数据

        Returns:
            dict: 包含聊天响应的字典
        """
        # 实现特定于聊天的运行逻辑
        return {"response": "Chat response"}

    def post_process(self, inference_result):
        """
        对聊天机器人的推断结果进行后处理。

        Args:
            inference_result (Any): 聊天机器人的推断结果。

        Returns:
            Any: 后处理后的推断结果。

        """
        # 实现特定于聊天的后处理
        return inference_result


# 启动应用
if __name__ == "__main__":
    # 注册处理器
    HandlerFactory.register_handler("/chat",
                                    ChatAppHandler,
                                    ChatHandler,
                                    request_context=ChatRequest,
                                    response_context=ChatResponse)
    start_app()
