# 设计思路

将 `fastapi` 框架抽象成标准的动作，分别为初始化、参数前处理、执行过程、参数后处理四个标准动作，业务只需要将其按照标准动作进行实现即可。

最后通过接口注册即可完成一个 `fastapi` 的接口暴露。

# 快速开始

```shell
# clone本仓库
git clone https://github.com/May-Yaha/web-service-fastapi.git 

# 安装依赖
cd web-service-fastapi
pip install -e .
```

# 使用说明

引入框架核心包：

```python
from yaha.web_api.web_service import ConfigHandler, RequestHandler, start_app
from yaha.web_api.factory import HandlerFactory
```

初始化方法：

```python

class Chatglm3Config(ConfigHandler):
    """
    Config handler for OpenAI API.
    """

    def initialize(self):
        """
        Initialize the config handler for OpenAI API.
        """
        
        # 在这里做你任意想做的事情
```

业务逻辑处理：

```python
class ChatGLM3ModelService(RequestHandler):
    """
    Chat completion service for OpenAI API.
    """

    def pre_process(self, request_body):
        """
        Pre-process request body for OpenAI API.
        """

        # 做你的逻辑处理
        return messages

    def run(self, processed_input):
        """
        Run the chat completion service for OpenAI API.
        """

        # 做你的逻辑处理

        return response

    def post_process(self, inference_result):
        """
        Post the inference result for OpenAI API.
        """
        return {
            "context": inference_result
        }

```

注册接口进行服务暴露：

```python
if __name__ == "__main__":
    HandlerFactory.register_handler("/v1/chat/completions",
                                    Chatglm3Config,
                                    ChatGLM3ModelService,
                                    request_context=ChatRequest,
                                    response_context=ChatResponse)
    app = start_app()
```