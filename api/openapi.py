"""
ChatGLM-3 OpenAI API.
"""
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from yaha.web_api.web_service import ConfigHandler, RequestHandler, start_app
from yaha.web_api.factory import HandlerFactory


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


class Chatglm3Config(ConfigHandler):
    """
    Config handler for OpenAI API.
    """

    def initialize(self):
        """
        Initialize the config handler for OpenAI API.
        """
        model_dir = "model/Qwen1.5-0.5B-Chat"
        self.device = "mps"

        self.model = AutoModelForCausalLM.from_pretrained(model_dir, device_map=self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir, device=self.device)
        if self.model is None or self.tokenizer is None:
            raise ValueError("Model or tokenizer is not properly initialized")


class ChatGLM3ModelService(RequestHandler):
    """
    Chat completion service for OpenAI API.
    """

    def pre_process(self, request_body):
        """
        Pre-process request body for OpenAI API.
        """

        if "prompt" not in request_body:
            return None

        messages = [
            {"role": "system", "content": "你是一个有用的助手。"},
            {"role": "user", "content": request_body["prompt"]}
        ]

        return messages

    def run(self, processed_input):
        """
        Run the chat completion service for OpenAI API.
        """

        text = self.app_config.tokenizer.apply_chat_template(
            processed_input,
            tokenize=False,
            add_generation_prompt=True
        )

        model_inputs = self.app_config.tokenizer([text], return_tensors="pt").to(self.app_config.device)

        generated_ids = self.app_config.model.generate(
            model_inputs.input_ids,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.app_config.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return response

    def post_process(self, inference_result):
        """
        Post the inference result for OpenAI API.
        """
        return {
            "context": inference_result
        }


if __name__ == "__main__":
    HandlerFactory.register_handler("/v1/chat/completions",
                                    Chatglm3Config,
                                    ChatGLM3ModelService,
                                    request_context=ChatRequest,
                                    response_context=ChatResponse)
    app = start_app()
