from transformers import PreTrainedModel, PreTrainedTokenizer


def process_chatglm_messages(messages, tools=None):
    """
    Processes a list of messages to be used in the chatglm3.
    """
    _messages = messages
    messages = []
    if tools:
        messages.append(
            {
                "role": "system",
                "content": "Answer the following questions as best as you can. You have access to the following tools:",
                "tools": tools
            }
        )

    for m in _messages:
        role, content, func_call = m.role, m.content, m.function_call
        if role == "function":
            messages.append(
                {
                    "role": "observation",
                    "content": content
                }
            )

        elif role == "assistant" and func_call is not None:
            for response in content.split("<|assistant|>"):
                metadata, sub_content = response.split("\n", maxsplit=1)
                messages.append(
                    {
                        "role": role,
                        "metadata": metadata,
                        "content": sub_content.strip()
                    }
                )
        else:
            messages.append({"role": role, "content": content})
    return messages


def generate_chatglm3(model: PreTrainedModel, tokenizer: PreTrainedTokenizer, params: dict):
    """
    Generate stream chatglm3 response.
    """
    messages = params["messages"]
    tools = params["tools"]
    temperature = float(params.get("temperature", 1.0))
    repetition_penalty = float(params.get("repetition_penalty", 1.0))
    max_new_tokens = int(params.get("max_tokens", 256))
    messages = process_chatglm_messages(messages, tools=tools)
    query, role = messages[-1]["content"], messages[-1]["role"]

    # total_len = 0
    inputs = tokenizer.build_chat_input(query, history=messages[-4:-1], role=role)
    input_ids = inputs.input_ids.cuda()
    attention_mask = inputs.attention_mask.cuda()
    position_ids = None

    eos_token_id = [tokenizer.eos_token_id, tokenizer.get_command("<|user|>"),
                    tokenizer.get_command("<|observation|>")]

    outputs = model.generate(input_ids=input_ids,
                             attention_mask=attention_mask,
                             position_ids=position_ids,
                             pad_token_id=tokenizer.eos_token_id,
                             eos_token_id=eos_token_id,
                             use_cache=True,
                             max_new_tokens=max_new_tokens,
                             repetition_penalty=repetition_penalty,
                             do_sample=False,
                             decoding_kwargs={'use_lookahead': True}
                             )
    output_ids = outputs
    input_length = input_ids.size(-1)
    output_ids = output_ids[:, input_length:].tolist()
    output_texts = []
    output_id_list = []
    completion_tokens_list = []

    for token_ids in output_ids:
        output_id_list.append(token_ids)
        text = tokenizer.decode(token_ids)
        output_texts.append(text)
        completion_tokens_list.append(len(token_ids))

    # 假设您只关心第一个输出
    completion_tokens = completion_tokens_list[0] if completion_tokens_list else 0

    return {
        "text": output_texts[0] if output_texts else "",
        "usage": {
            "prompt_tokens": input_length,
            "completion_tokens": completion_tokens,
            "total_tokens": input_length + completion_tokens,
        },
        "finish_reason": "function_call",
    }
