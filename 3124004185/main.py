#这个版本先列好程序大纲

import sys


def read_file(file_path):
    """读取文件内容，返回字符串。"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def calculate_similarity(text1, text2):
    """计算两段文本的相似度，返回 0.00 ~ 1.00 之间的浮点数。

    当前为占位实现，后续版本会替换为真正的查重算法。
    """
    return 0.00


def write_result(file_path, similarity):
    """将相似度结果写入答案文件，保留两位小数。"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"{similarity:.2f}")


def main():
    # 参数数量校验：程序名 + 3 个路径 = 4 个参数
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