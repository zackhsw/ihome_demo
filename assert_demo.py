def num_div(num1, num2):
    # assert 断言  后面是一个表达式，如果表达式返回真，断言成功，程序继续执行
    # 断言抛出异常AssertionError， 终止程序继续往下执行
    assert isinstance(num1, int)
    assert isinstance(num2, int)
    assert num2 != 0

    print(num1 / num2)


if __name__ == '__main__':
    num_div(100,0)
