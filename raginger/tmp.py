from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer

# 1. 加载你指定模型的分词器
tokenizer = AutoTokenizer.from_pretrained("models/google/embeddinggemma-300m")

# 2. 定义一个长度计算函数
def token_len(text):
    tokens = tokenizer.encode(text, add_special_tokens=False)
    return len(tokens)

# 3. 初始化分块器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=256,
    chunk_overlap=25,
    length_function=token_len, # 使用自定义的 Token 长度计算函数
    separators=["\n\n", "\n", "。", "！", "？", "；"]
    # separators=["\n\n", "\n", " ", ""] # 优先级：段落 > 换行 > 空格 > 字符
)

# 4. 执行分块
text = """量子计算作为下一代计算技术的核心，近年来取得了多项突破性进展。2025年，中国科学家成功研制出拥有512个量子比特的超导量子计算机原型机，实现了量子霸权。该计算机能够在200秒内完成传统超级计算机需要一万年才能解决的特定数学问题。量子计算的原理基于量子叠加与纠缠态，量子比特可同时处于0和1状态，从而并行处理海量数据。然而，量子态的退相干效应仍是主要挑战，当前系统需在接近绝对零度的环境下运行。未来五年，量子纠错码和拓扑量子计算有望推动实用化进程。预计到2030年，量子计算将在密码学、新药研发、气候模拟和人工智能训练等领域产生颠覆性影响。科技巨头与初创企业纷纷布局，中美欧之间的竞争日趋激烈。此外，量子通信网络也已初步建成，京沪干线实现了千公里级的量子密钥分发。量子时代的到来将重塑信息技术的底层逻辑，我们正站在新纪元的门槛上。"""
chunks = text_splitter.split_text(text)
print(chunks)