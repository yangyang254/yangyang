import unittest
import os
import sys
import tempfile
import subprocess
from main import (
    preprocess, get_ngrams, calculate_similarity,
    read_file, write_result,
    FileReadError, FileWriteError, parse_args
)
from unittest.mock import patch, mock_open

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


class TestFileIO(unittest.TestCase):
    """测试文件读写函数"""

    def setUp(self):
        """每个测试前创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """每个测试后清理临时文件"""
        for f in os.listdir(self.temp_dir):
            p = os.path.join(self.temp_dir, f)
            if os.path.isfile(p):
                os.remove(p)
        os.rmdir(self.temp_dir)

    def test_read_file_normal(self):
        """正常读取文件内容"""
        path = os.path.join(self.temp_dir, "test.txt")
        with open(path, 'w', encoding='utf-8') as f:
            f.write("测试内容")
        self.assertEqual(read_file(path), "测试内容")

    def test_read_file_not_exist(self):
        """读取不存在的文件应抛出 FileReadError"""
        with self.assertRaises(FileReadError):
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
        result = subprocess.run(
            ["python", "main.py", "only_one_arg.txt"],
            capture_output=True, text=True
        )
        self.assertNotEqual(result.returncode, 0)

    def test_nonexistent_input_file(self):
        """输入文件不存在时应抛出异常"""
        result = subprocess.run(
            ["python", "main.py", "not_exist1.txt", "not_exist2.txt", "ans.txt"],
            capture_output=True, text=True
        )
        self.assertNotEqual(result.returncode, 0)


class TestExceptions(unittest.TestCase):
    """测试各种异常场景"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        for f in os.listdir(self.temp_dir):
            p = os.path.join(self.temp_dir, f)
            if os.path.isfile(p):
                os.remove(p)
        os.rmdir(self.temp_dir)

    def test_read_dir_as_file(self):
        """把目录当成文件读取，应抛 FileReadError"""
        with self.assertRaises(FileReadError):
            read_file(self.temp_dir)

    def test_read_file_wrong_encoding(self):
        """非 UTF-8 编码文件应抛 FileReadError"""
        path = os.path.join(self.temp_dir, "gbk.txt")
        # 直接用二进制写入非法 UTF-8 字节序列
        with open(path, 'wb') as f:
            f.write(b'\xff\xfe\x00\x00invalid utf-8')
        with self.assertRaises(FileReadError):
            read_file(path)

    def test_write_to_invalid_dir(self):
        """写入不存在的目录应抛 FileWriteError"""
        bad_path = os.path.join(self.temp_dir, "not_exist_dir", "ans.txt")
        with self.assertRaises(FileWriteError):
            write_result(bad_path, 0.5)

    def test_parse_args_too_few(self):
        """参数不足应抛 ValueError"""
        with self.assertRaises(ValueError):
            parse_args(["main.py", "a.txt"])

    def test_parse_args_too_many(self):
        """参数过多应抛 ValueError"""
        with self.assertRaises(ValueError):
            parse_args(["main.py", "a.txt", "b.txt", "c.txt", "d.txt"])

    def test_parse_args_normal(self):
        """正常参数应正确解析"""
        result = parse_args(["main.py", "a.txt", "b.txt", "c.txt"])
        self.assertEqual(result, ("a.txt", "b.txt", "c.txt"))


if __name__ == '__main__':
    unittest.main()


class TestExceptionBranches(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.path = os.path.join(self.temp_dir, "f.txt")
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write("test")

    def tearDown(self):
        for f in os.listdir(self.temp_dir):
            p = os.path.join(self.temp_dir, f)
            if os.path.isfile(p):
                os.remove(p)
        os.rmdir(self.temp_dir)

    def test_read_file_permission_error(self):
        """读取文件无权限时应抛 FileReadError"""
        with patch("builtins.open", side_effect=PermissionError("denied")):
            with self.assertRaises(FileReadError):
                read_file(self.path)

    def test_read_file_os_error(self):
        """读取文件发生 OSError 时应抛 FileReadError"""
        with patch("builtins.open", side_effect=OSError("disk error")):
            with self.assertRaises(FileReadError):
                read_file(self.path)

    def test_write_file_permission_error(self):
        """写入文件无权限时应抛 FileWriteError"""
        with patch("builtins.open", side_effect=PermissionError("denied")):
            with self.assertRaises(FileWriteError):
                write_result(self.path, 0.5)

    def test_write_file_os_error(self):
        """写入文件发生 OSError 时应抛 FileWriteError"""
        with patch("builtins.open", side_effect=OSError("disk full")):
            with self.assertRaises(FileWriteError):
                write_result(self.path, 0.5)

    def test_main_success(self):
        """正常流程应打印查重结果"""
        import main as m
        argv = ["main.py", self.path, self.path, os.path.join(self.temp_dir, "ans.txt")]
        with patch.object(sys, "argv", argv):
            try:
                m.main()
            except SystemExit:
                self.fail("main() 不应退出")

    def test_main_value_error(self):
        """参数错误时 main() 应以退出码 1 退出"""
        import main as m
        with patch.object(sys, "argv", ["main.py", "a.txt"]):
            with self.assertRaises(SystemExit) as cm:
                m.main()
            self.assertEqual(cm.exception.code, 1)

    def test_main_read_error(self):
        """读取错误时 main() 应以退出码 2 退出"""
        import main as m
        argv = ["main.py", "not_exist.txt", "not_exist.txt", "ans.txt"]
        with patch.object(sys, "argv", argv):
            with self.assertRaises(SystemExit) as cm:
                m.main()
            self.assertEqual(cm.exception.code, 2)

    def test_main_write_error(self):
        """写入错误时 main() 应以退出码 3 退出"""
        import main as m
        bad_ans = os.path.join(self.temp_dir, "no_dir", "ans.txt")
        argv = ["main.py", self.path, self.path, bad_ans]
        with patch.object(sys, "argv", argv):
            with self.assertRaises(SystemExit) as cm:
                m.main()
            self.assertEqual(cm.exception.code, 3)

    def test_main_unknown_error(self):
        """未知异常时 main() 应以退出码 9 退出"""
        import main as m
        argv = ["main.py", self.path, self.path, os.path.join(self.temp_dir, "ans.txt")]
        with patch.object(sys, "argv", argv):
            with patch.object(m, "calculate_similarity", side_effect=RuntimeError("boom")):
                with self.assertRaises(SystemExit) as cm:
                    m.main()
                self.assertEqual(cm.exception.code, 9)