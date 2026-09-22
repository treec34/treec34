import argparse
import random
import re
from fractions import Fraction
import sys

# 定义支持的运算符
OPERATORS = ['+', '-', '×', '÷']


class Node:
    """定义表达式的抽象语法树（AST）节点"""

    def __init__(self, op=None, left=None, right=None, value=None):
        self.op = op
        self.left = left
        self.right = right
        self.value = value

    def is_leaf(self):
        # 修正：判断是否为叶子节点的唯一标准是没有操作符
        return self.op is None

    def to_string(self):
        """将AST转换为带括号的数学表达式字符串"""
        if self.is_leaf():
            return format_fraction(self.value)

        left_str = self.left.to_string()
        right_str = self.right.to_string()

        # 处理括号逻辑：如果父节点是乘除，子节点是加减，则必须加括号
        if self.op in ['×', '÷']:
            if not self.left.is_leaf() and self.left.op in ['+', '-']:
                left_str = f"({left_str})"
            if not self.right.is_leaf() and self.right.op in ['+', '-']:
                right_str = f"({right_str})"

        # 处理同级运算的右结合括号，避免 1 - (2 + 3) 的歧义
        if self.op == '-':
            if not self.right.is_leaf() and self.right.op in ['+', '-']:
                right_str = f"({right_str})"
        if self.op == '÷':
            if not self.right.is_leaf() and self.right.op in ['×', '÷']:
                right_str = f"({right_str})"

        return f"{left_str} {self.op} {right_str}"


def format_fraction(f):
    """将Fraction对象格式化为题目要求的带分数形式"""
    if f.denominator == 1:
        return str(f.numerator)
    if f.numerator > f.denominator:
        whole = f.numerator // f.denominator
        remainder = f.numerator % f.denominator
        return f"{whole}'{remainder}/{f.denominator}"
    return f"{f.numerator}/{f.denominator}"


def generate_random_fraction(max_val):
    """生成范围内的随机自然数或真分数/带分数，严格保证数值小于 max_val"""
    if random.random() > 0.5:
        # 生成自然数: [0, max_val - 1]
        return Fraction(random.randint(0, max_val - 1), 1)
    else:
        # 保证分母在合规范围内，最小为2
        den_max = max_val - 1 if max_val > 2 else 2
        denominator = random.randint(2, den_max)
        # 限制分子大小，确保最终分数值严格小于 max_val
        numerator = random.randint(1, max_val * denominator - 1)
        return Fraction(numerator, denominator)


def collect_operands(node, op):
    """收集连续相同运算符的节点，用于去重规范化"""
    if node.is_leaf() or node.op != op:
        return [node]
    return collect_operands(node.left, op) + collect_operands(node.right, op)


def get_canonical(node):
    """生成表达式的标准化字符串，用于检测重复题目"""
    if node.is_leaf():
        return str(node.value)

    if node.op in ['+', '×']:
        # 满足交换律和结合律，收集所有操作数并排序比对
        operands = collect_operands(node, node.op)
        canon_strs = sorted([get_canonical(n) for n in operands])
        return f"{node.op}(" + ",".join(canon_strs) + ")"
    else:
        left_canon = get_canonical(node.left)
        right_canon = get_canonical(node.right)
        return f"{node.op}({left_canon},{right_canon})"


def generate_ast(num_ops, max_val):
    """递归生成合法的抽象语法树"""
    if num_ops == 0:
        return Node(value=generate_random_fraction(max_val))

    op = random.choice(OPERATORS)
    left_ops = random.randint(0, num_ops - 1)
    right_ops = num_ops - 1 - left_ops

    while True:
        left = generate_ast(left_ops, max_val)
        right = generate_ast(right_ops, max_val)

        # 计算当前节点的值，验证强制性约束条件
        if op == '+':
            val = left.value + right.value
        elif op == '-':
            if left.value < right.value:
                # 确保计算过程不产生负数
                left, right = right, left
            val = left.value - right.value
        elif op == '×':
            val = left.value * right.value
        elif op == '÷':
            if right.value == 0:
                continue
            val = left.value / right.value
            # 依据要求：除法子表达式的结果必须为真分数（严格小于1）
            if val >= 1:
                continue

        node = Node(op=op, left=left, right=right)
        node.value = val
        return node


def parse_and_eval(expr_str):
    """解析并计算字符串表达式（用于判卷程序）"""
    expr_str = expr_str.replace('×', '*').replace('÷', '/')
    expr_str = re.sub(r'(\d+)\'(\d+)/(\d+)', r'(\1+Fraction(\2,\3))', expr_str)
    expr_str = re.sub(r'(\d+)/(\d+)', r'Fraction(\1,\2)', expr_str)

    if '=' in expr_str:
        expr_str = expr_str.split('=')[0]

    return eval(expr_str, {"Fraction": Fraction})


def format_answer(ans_str):
    """规范化待判定的答案字符串"""
    if ans_str.strip() == "": return ""
    ans_str = ans_str.strip()
    try:
        val = parse_and_eval(ans_str)
        return format_fraction(val)
    except:
        return ans_str


def main():
    parser = argparse.ArgumentParser(description="小学四则运算自动生成器")
    parser.add_argument('-n', type=int, help='生成题目的个数')
    parser.add_argument('-r', type=int, help='题目数值的最大范围（必须大于0）')
    parser.add_argument('-e', type=str, help='需判定的题目文件路径')
    parser.add_argument('-a', type=str, help='需判定的答案文件路径')
    args = parser.parse_args()

    # 判题逻辑
    if args.e and args.a:
        try:
            with open(args.e, 'r', encoding='utf-8') as fe, open(args.a, 'r', encoding='utf-8') as fa:
                exercises = fe.readlines()
                answers = fa.readlines()
        except FileNotFoundError as e:
            print(f"找不到文件: {e}")
            return

        correct = []
        wrong = []

        for i, (ex, ans) in enumerate(zip(exercises, answers), 1):
            try:
                ans_val_str = ans.split('.')[-1].strip()
                ans_formatted = format_answer(ans_val_str)

                ex_str = ex.split('.')[1].strip()
                real_val = parse_and_eval(ex_str)
                real_formatted = format_fraction(real_val)

                if ans_formatted == real_formatted:
                    correct.append(i)
                else:
                    wrong.append(i)
            except Exception:
                wrong.append(i)

        with open("Grade.txt", "w", encoding='utf-8') as f:
            f.write(f"Correct: {len(correct)} ({', '.join(map(str, correct))})\n")
            f.write(f"Wrong: {len(wrong)} ({', '.join(map(str, wrong))})\n")
        print("判卷完成，结果已输出到 Grade.txt")
        return

    # 生成逻辑
    if args.n is not None and args.r is not None:
        if args.r <= 0 or args.n <= 0:
            print("错误：范围 -r 和 题目数 -n 必须为大于0的自然数。")
            return

        exercises = []
        answers = []
        seen = set()

        print(f"正在生成 {args.n} 道题目，最大范围 {args.r}，请稍候...")
        while len(exercises) < args.n:
            num_ops = random.randint(1, 3)
            ast = generate_ast(num_ops, args.r)

            canon = get_canonical(ast)
            if canon in seen:
                continue
            seen.add(canon)

            expr_str = ast.to_string()
            exercises.append(f"{len(exercises) + 1}. {expr_str} = ")
            answers.append(f"{len(answers) + 1}. {format_fraction(ast.value)}")

        with open("Exercises.txt", "w", encoding='utf-8') as f:
            f.write("\n".join(exercises))
        with open("Answers.txt", "w", encoding='utf-8') as f:
            f.write("\n".join(answers))
        print("生成完成！题目在 Exercises.txt，答案在 Answers.txt。")
    else:
        print(
            "参数错误！\n生成题目: python main.py -n <题目数量> -r <数值范围>\n判定答案: python main.py -e <题目文件> -a <答案文件>")


if __name__ == "__main__":
    main()