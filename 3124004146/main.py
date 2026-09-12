import sys
import math
import jieba
from collections import Counter


# 1. 读取文件
def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            if not text.strip():
                raise ValueError(f"文件内容为空: {file_path}")
            return text
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
        sys.exit(1)


# 2. 提取文本特征向量（TF词频）
def get_tf_vector(text):
    # 使用 jieba 进行精确模式中文分词
    words = list(jieba.cut(text))
    # 使用 Counter 统计每个词汇出现的次数
    return Counter(words)


# 3. 计算余弦相似度
def cosine_similarity(vec1, vec2):
    # 找出所有的唯一词汇
    words = set(vec1.keys()).union(set(vec2.keys()))

    # 计算点积
    dot_product = sum(vec1.get(word, 0) * vec2.get(word, 0) for word in words)

    # 计算两个向量的模
    mag1 = math.sqrt(sum(vec1.get(word, 0) ** 2 for word in words))
    mag2 = math.sqrt(sum(vec2.get(word, 0) ** 2 for word in words))

    # 避免除以 0 的异常
    if mag1 * mag2 == 0:
        return 0.0

    return dot_product / (mag1 * mag2)


if __name__ == '__main__':
    # 异常处理：参数数量不对
    if len(sys.argv) != 4:
        print("用法: python main.py [原文文件] [抄袭版论文的文件] [答案文件]")
        sys.exit(1)

    orig_path = sys.argv[1]
    copy_path = sys.argv[2]
    ans_path = sys.argv[3]

    # 执行主逻辑
    orig_text = read_file(orig_path)
    copy_text = read_file(copy_path)

    tf_orig = get_tf_vector(orig_text)
    tf_copy = get_tf_vector(copy_text)

    similarity = cosine_similarity(tf_orig, tf_copy)

    # 写入答案文件
    try:
        with open(ans_path, 'w', encoding='utf-8') as f:
            # 格式化为两位小数输出
            f.write(f"{similarity:.2f}\n")
    except Exception as e:
        print(f"写入答案文件时发生错误: {e}")
        sys.exit(1)