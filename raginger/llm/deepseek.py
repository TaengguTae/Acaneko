from basellm import BaseLLM


class Deepseek(BaseLLM):
    """
    DeepSeek LLM
    """
    def __init__(self, api_key: str, base_url: str, model: str):
        super().__init__(api_key, base_url, model)

    def get_response(
        self, 
        user_message: str, 
        system_prompt: str = "You are a cute assistant called Acaneko.",
        temperature: float = 1.0,
        top_p: float = 0.9,
        stream: bool = False,
    ) -> str:
        """获取响应"""
        return self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}   
            ],
            temperature=temperature,
            top_p=top_p,
            stream=stream
        ).choices[0].message.content


if __name__ == "__main__":
    llm = Deepseek(
        api_key="sk-ecbfbfea56334565988db0d79b3e253c", 
        base_url="https://api.deepseek.com/v1", 
        model="deepseek-chat"
    )
    print(llm.get_response("你好"))
           
