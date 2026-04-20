from openai import OpenAI


class BaseLLM:
    """
    基础LLM
    """
    def __init__(self, api_key: str, base_url: str, model: str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def get_response(self, query: str) -> str:
        """
        获取响应
        """
        pass

    def call(self, query: str) -> str:
        """
        调用LLM
        """
        pass


