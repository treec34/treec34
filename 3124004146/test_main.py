import unittest
from main import get_tf_vector, cosine_similarity


class TestPaperCheck(unittest.TestCase):

    def test_identical_text(self):
        # 测试：完全相同的文本，期望值为 1.0
        txt1 = get_tf_vector("软件工程是一门实践性很强的学科")
        txt2 = get_tf_vector("软件工程是一门实践性很强的学科")
        sim = cosine_similarity(txt1, txt2)
        self.assertAlmostEqual(sim, 1.0, places=2)

    def test_totally_different(self):
        # 测试：完全不相关的文本，期望值为 0.0
        txt1 = get_tf_vector("今天天气不错")
        txt2 = get_tf_vector("我喜欢吃苹果")
        sim = cosine_similarity(txt1, txt2)
        self.assertEqual(sim, 0.0)

    def test_partial_overlap(self):
        # 测试：部分抄袭修改，期望值在 (0, 1) 之间
        txt1 = get_tf_vector("今天是星期天，天气晴，今天晚上我要去看电影。")
        txt2 = get_tf_vector("今天是周天，天气晴朗，我晚上要去看电影。")
        sim = cosine_similarity(txt1, txt2)
        self.assertTrue(0.5 < sim < 0.99)