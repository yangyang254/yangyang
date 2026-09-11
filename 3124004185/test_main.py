import unittest
import os
import tempfile
from main import preprocess, get_ngrams, calculate_similarity


class TestPreprocess(unittest.TestCase):
    """测试文本预处理函数"""

    def test_preprocess_lowercase(self):
        """大写字母应被转为小写"""
        self.assertEqual(preprocess("Hello World"), "helloworld")

    def test_preprocess_remove_punctuation(self):
        """标点符号和空格应被去除"""
        self.assertEqual(preprocess("你好，世界！"), "你好世界")

    def test_preprocess_empty(self):
        """空字符串应返回空字符串"""
        self.assertEqual(preprocess(""), "")


class TestGetNgrams(unittest.TestCase):
    """测试 n-gram 生成函数"""

    def test_get_ngrams_normal(self):
        """正常文本应生成正确的 2-gram 集合"""
        result = get_ngrams("abcd", 2)
        self.assertEqual(result, {("a", "b"), ("b", "c"), ("c", "d")})

    def test_get_ngrams_short_text(self):
        """文本长度不足 n 时应返回空集合"""
        self.assertEqual(get_ngrams("a", 2), set())

    def test_get_ngrams_repeated(self):
        """重复字符应正确去重"""
        result = get_ngrams("aaaa", 2)
        self.assertEqual(result, {("a", "a")})


class TestCalculateSimilarity(unittest.TestCase):
    """测试相似度计算函数"""

    def test_identical_text(self):
        """完全相同的文本，相似度应为 1.00"""
        text = "今天是星期天，天气晴。"
        self.assertAlmostEqual(calculate_similarity(text, text), 1.00, places=2)

    def test_completely_different(self):
        """完全不同的文本，相似度应接近 0"""
        sim = calculate_similarity("abcde", "12345")
        self.assertLess(sim, 0.1)

    def test_both_empty(self):
        """两个空文本，相似度应为 0.00"""
        self.assertEqual(calculate_similarity("", ""), 0.00)

    def test_partial_similarity(self):
        """部分相似的文本，相似度应在 0 和 1 之间"""
        sim = calculate_similarity("今天是星期天", "今天是周天")
        self.assertGreater(sim, 0.0)
        self.assertLess(sim, 1.0)

    def test_case_insensitive(self):
        """大小写不同但内容相同，相似度应为 1.00"""
        sim = calculate_similarity("Hello World", "hello world")
        self.assertAlmostEqual(sim, 1.00, places=2)


if __name__ == '__main__':
    unittest.main()

from main import read_file, write_result


class TestFileIO(unittest.TestCase):
    """测试文件读写函数"""

    def setUp(self):
        """每个测试前创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """每个测试后清理临时文件"""
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)

    def test_read_file_normal(self):
        """正常读取文件内容"""
        path = os.path.join(self.temp_dir, "test.txt")
        with open(path, 'w', encoding='utf-8') as f:
            f.write("测试内容")
        self.assertEqual(read_file(path), "测试内容")

    def test_read_file_not_exist(self):
        """读取不存在的文件应抛出 FileNotFoundError"""
        with self.assertRaises(FileNotFoundError):
            read_file(os.path.join(self.temp_dir, "not_exist.txt"))

    def test_write_result_format(self):
        """写入结果应保留两位小数"""
        path = os.path.join(self.temp_dir, "ans.txt")
        write_result(path, 0.5)
        with open(path, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), "0.50")

    def test_write_result_rounding(self):
        """写入结果应正确四舍五入"""
        path = os.path.join(self.temp_dir, "ans.txt")
        write_result(path, 0.456)
        with open(path, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), "0.46")


class TestCommandLineArgs(unittest.TestCase):
    """测试命令行参数处理"""

    def test_missing_args(self):
        """参数数量不足时应退出并返回非0状态码"""
        import subprocess
        result = subprocess.run(
            ["python", "main.py", "only_one_arg.txt"],
            capture_output=True, text=True
        )
        self.assertNotEqual(result.returncode, 0)

    def test_nonexistent_input_file(self):
        """输入文件不存在时应抛出异常"""
        import subprocess
        result = subprocess.run(
            ["python", "main.py", "not_exist1.txt", "not_exist2.txt", "ans.txt"],
            capture_output=True, text=True
        )
        self.assertNotEqual(result.returncode, 0)