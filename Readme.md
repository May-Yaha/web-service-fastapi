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

# 日志打印样式

```python
==> logs/web_service.log <==
[2024-02-07 16:17:06,436] [pid:80550] [level:INFO] [logid:17072938263441553] [CPU: 31.8] [Memory: 93.2] [GPU: 0] Pre processed: [{'role': 'system', 'content': '你是一个有用的助手。'}, {'role': 'user', 'content': '你好'}] 
[2024-02-07 16:17:09,555] [pid:80550] [level:INFO] [logid:17072938263441553] [CPU: 31.9] [Memory: 95.2] [GPU: 0] Inference result: 你好！有什么我能帮助你的吗？ 
[2024-02-07 16:17:13,939] [pid:80550] [level:INFO] [logid:17072938339121506] [CPU: 36.5] [Memory: 94.4] [GPU: 0] Request handler type: /v1/chat/completions 
[2024-02-07 16:17:13,961] [pid:80550] [level:INFO] [logid:17072938339121506] [CPU: 0.0] [Memory: 94.4] [GPU: 0] Request body: <starlette.requests.Request object at 0x7faa9fc8b490>, Parse Params: {'prompt': '你好'} 
[2024-02-07 16:17:13,982] [pid:80550] [level:INFO] [logid:17072938339121506] [CPU: 0.0] [Memory: 94.4] [GPU: 0] Pre processed: [{'role': 'system', 'content': '你是一个有用的助手。'}, {'role': 'user', 'content': '你好'}] 
[2024-02-07 16:17:17,365] [pid:80550] [level:INFO] [logid:17072938339121506] [CPU: 48.3] [Memory: 95.7] [GPU: 0] Inference result: 你好！有什么我可以帮助你的吗？ 
[2024-02-07 16:17:19,704] [pid:80550] [level:INFO] [logid:17072938396705887] [CPU: 30.0] [Memory: 93.7] [GPU: 0] Request handler type: /v1/chat/completions 
[2024-02-07 16:17:19,725] [pid:80550] [level:INFO] [logid:17072938396705887] [CPU: 16.7] [Memory: 93.6] [GPU: 0] Request body: <starlette.requests.Request object at 0x7faa9fc8ba90>, Parse Params: {'prompt': '你好'} 
[2024-02-07 16:17:19,748] [pid:80550] [level:INFO] [logid:17072938396705887] [CPU: 0.0] [Memory: 93.5] [GPU: 0] Pre processed: [{'role': 'system', 'content': '你是一个有用的助手。'}, {'role': 'user', 'content': '你好'}] 
[2024-02-07 16:17:22,977] [pid:80550] [level:INFO] [logid:17072938396705887] [CPU: 27.9] [Memory: 95.6] [GPU: 0] Inference result: 你好！有什么我可以帮到你的吗？ 

==> logs/web_service.log.wf <==
[2024-02-07 15:38:40,810] [pid:74903] [level:ERROR] [logid:170729152074818] [CPU: 0.0] [Memory: 95.1] [GPU: 0] Failed to process request: 'Qwen2TokenizerFast' object has no attribute 'build_chat_input' 
[2024-02-07 15:45:27,208] [pid:75707] [level:ERROR] [logid:17072919271303337] [CPU: 0.0] [Memory: 94.9] [GPU: 0] Failed to process request: 'Qwen2Model' object has no attribute 'chat' 
[2024-02-07 15:46:49,708] [pid:75907] [level:ERROR] [logid:17072920096178218] [CPU: 25.0] [Memory: 93.6] [GPU: 0] Failed to process request: 'Qwen2ForCausalLM' object has no attribute 'chat' 
[2024-02-07 15:55:58,790] [pid:78374] [level:ERROR] [logid:default] [CPU: 0.0] [Memory: 91.5] [GPU: 0] Failed to initialize config: Tokenizer class Qwen2Tokenizer does not exist or is not currently imported. 
[2024-02-07 15:56:38,828] [pid:78453] [level:ERROR] [logid:default] [CPU: 0.0] [Memory: 91.7] [GPU: 0] Failed to initialize config: Tokenizer class Qwen2Tokenizer does not exist or is not currently imported. 
[2024-02-07 16:00:18,849] [pid:78834] [level:ERROR] [logid:default] [CPU: 0.0] [Memory: 91.4] [GPU: 0] Failed to initialize config: Tokenizer class Qwen2Tokenizer does not exist or is not currently imported. 
[2024-02-07 16:06:03,672] [pid:79404] [level:ERROR] [logid:default] [CPU: 0.0] [Memory: 90.9] [GPU: 0] Failed to initialize config: 'qwen2' 
[2024-02-07 16:06:46,355] [pid:79471] [level:ERROR] [logid:default] [CPU: 22.2] [Memory: 91.0] [GPU: 0] Failed to initialize config: 'qwen2' 
[2024-02-07 16:08:16,529] [pid:79642] [level:ERROR] [logid:default] [CPU: 10.0] [Memory: 90.9] [GPU: 0] Failed to initialize config: 'qwen2' 
[2024-02-07 16:12:48,695] [pid:80158] [level:ERROR] [logid:17072935685806808] [CPU: 22.2] [Memory: 95.1] [GPU: 0] Failed to process request: 'Qwen2ForCausalLM' object has no attribute 'chat'
```