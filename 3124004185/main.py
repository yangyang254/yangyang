import sys
import re


# 模块级别预编译正则，避免每次调用都重新编译
CLEAN_PATTERN = re.compile(r'[^\w]')


def read_file(file_path):
    """读取文件内容，返回字符串。"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def preprocess(text):
    """文本预处理：转小写，去掉标点符号和空白字符。

    使用预编译的 CLEAN_PATTERN，避免重复编译正则表达式。
    """
    return CLEAN_PATTERN.sub('', text.lower())


def get_ngrams(text, n=2):
    """生成字符级 n-gram 集合。

    使用 zip 一次性生成元组，避免使用字符串切片产生大量临时字符串。
    例如 text="abcd", n=2 -> {("a","b"), ("b","c"), ("c","d")}
    """
    if len(text) < n:
        return set()
    return set(zip(*(text[i:] for i in range(n))))


def calculate_similarity(text1, text2):
    """计算两段文本的相似度，使用字符 2-gram 的 Jaccard 相似度。"""
    p1 = preprocess(text1)
    p2 = preprocess(text2)

    if not p1 and not p2:
        return 0.00

    # 短文本退化为字符级集合比较
    if len(p1) < 2 or len(p2) < 2:
        set1, set2 = set(p1), set(p2)
    else:
        set1 = get_ngrams(p1, 2)
        set2 = get_ngrams(p2, 2)

    if not set1 and not set2:
        return 0.00

    # 短路优化：完全相同时直接返回 1.00
    if set1 == set2:
        return 1.00

    intersection = set1 & set2
    union = set1 | set2
    return len(intersection) / len(union)


def write_result(file_path, similarity):
    """将相似度结果写入答案文件，保留两位小数。"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"{similarity:.2f}")


def main():
    if len(sys.argv) != 4:
        print("用法: python main.py <原文文件> <抄袭版文件> <答案文件>")
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