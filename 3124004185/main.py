import sys
import re


def read_file(file_path):
    """读取文件内容，返回字符串。"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def preprocess(text):
    """文本预处理：转小写，去掉标点符号和空白字符。"""
    text = text.lower()
    text = re.sub(r'[^\w]', '', text)
    return text


def calculate_similarity(text1, text2):
    """计算两段文本的相似度，使用字符级 Jaccard 相似度。

    相似度 = |交集| / |并集|
    """
    set1 = set(preprocess(text1))
    set2 = set(preprocess(text2))

    if not set1 and not set2:
        return 0.00

    intersection = set1 & set2
    union = set1 | set2
    return len(intersection) / len(union)


def write_result(file_path, similarity):
    """将相似度结果写入答案文件，保留两位小数。"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"{similarity:.2f}")


def main():
    if len(sys.argv) != 4:
        print("用法: python main.py <s原文文件> <抄袭版文件> <答案文件>")
        sys.exit(1)

    orig_path = sys.argv[1]
    copy_path = sys.argv[2]
    ans_path = sys.argv[3]

    orig_text = read_file(orig_path)
    copy_text = read_file(copy_path)

    similarity = calculate_similarity(orig_text, copy_text)
    write_result(ans_path, similarity)


if __name__ == '__main__':
    main()