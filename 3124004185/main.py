import sys
import re
import os


# 模块级别预编译正则，避免每次调用都重新编译
CLEAN_PATTERN = re.compile(r'[^\w]')


class FileReadError(Exception):
    """读取文件失败时抛出的自定义异常"""
    pass


class FileWriteError(Exception):
    """写入文件失败时抛出的自定义异常"""
    pass


def read_file(file_path):
    """读取文件内容，返回字符串。

    异常：
        FileReadError: 文件不存在、不是文件、编码错误、无权限等。
    """
    if not os.path.exists(file_path):
        raise FileReadError(f"文件不存在: {file_path}")
    if not os.path.isfile(file_path):
        raise FileReadError(f"路径不是文件: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError as e:
        raise FileReadError(f"文件编码错误，请使用 UTF-8 编码: {file_path}") from e
    except PermissionError as e:
        raise FileReadError(f"无权限读取文件: {file_path}") from e
    except OSError as e:
        raise FileReadError(f"读取文件失败: {file_path} ({e})") from e


def write_result(file_path, similarity):
    """将相似度结果写入答案文件，保留两位小数。

    异常：
        FileWriteError: 目录不存在、无权限写入、磁盘满等。
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"{similarity:.2f}")
    except PermissionError as e:
        raise FileWriteError(f"无权限写入文件: {file_path}") from e
    except OSError as e:
        raise FileWriteError(f"写入文件失败: {file_path} ({e})") from e


def preprocess(text):
    """文本预处理：转小写，去掉标点符号和空白字符。"""
    return CLEAN_PATTERN.sub('', text.lower())


def get_ngrams(text, n=2):
    """生成字符级 n-gram 集合。"""
    if len(text) < n:
        return set()
    return set(zip(*(text[i:] for i in range(n))))


def calculate_similarity(text1, text2):
    """计算两段文本的相似度，使用字符 2-gram 的 Jaccard 相似度。"""
    p1 = preprocess(text1)
    p2 = preprocess(text2)

    if not p1 and not p2:
        return 0.00

    if len(p1) < 2 or len(p2) < 2:
        set1, set2 = set(p1), set(p2)
    else:
        set1 = get_ngrams(p1, 2)
        set2 = get_ngrams(p2, 2)

    if not set1 and not set2:
        return 0.00

    if set1 == set2:
        return 1.00

    intersection = set1 & set2
    union = set1 | set2
    return len(intersection) / len(union)


def parse_args(argv):
    """解析命令行参数，返回 (原文路径, 抄袭版路径, 答案路径)。

    异常：
        ValueError: 参数数量不对。
    """
    if len(argv) != 4:
        raise ValueError(
            "参数数量错误。用法: python main.py <原文文件> <抄袭版文件> <答案文件>"
        )
    return argv[1], argv[2], argv[3]


def main():
    try:
        orig_path, copy_path, ans_path = parse_args(sys.argv)
        orig_text = read_file(orig_path)
        copy_text = read_file(copy_path)
        similarity = calculate_similarity(orig_text, copy_text)
        write_result(ans_path, similarity)
        print(f"查重完成，相似度: {similarity:.2f}")
    except ValueError as e:
        print(f"[参数错误] {e}")
        sys.exit(1)
    except FileReadError as e:
        print(f"[读取错误] {e}")
        sys.exit(2)
    except FileWriteError as e:
        print(f"[写入错误] {e}")
        sys.exit(3)
    except Exception as e:
        print(f"[未知错误] {e}")
        sys.exit(9)


if __name__ == '__main__':
    main()