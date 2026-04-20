class Understander:
    """
    查询理解
    """

    def __init__(
        self,
        simple_mode: bool = False,
        need_keyword: bool = False,
        need_slot: bool = False,
        need_rewrite: bool = False,
        need_hyde: bool = False
    ):
        pass

    def build_prompt(self, query: str) -> str:
        """
        构建prompt
        """
        pass 

    def understand(self, query: str) -> dict:
        """
        理解查询
        """
        pass