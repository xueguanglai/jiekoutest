# 电商接口自动化测试框架

这是一个基于 `pytest + requests + allure` 的接口自动化测试项目，适合电商平台测试团队日常维护和扩展。

项目目标：

- 结构简单，方便新人上手
- 代码清晰，方便团队长期维护
- 支持环境切换
- 支持测试数据分离
- 支持 Allure 测试报告
- 支持后续扩展登录态、关联接口、批量执行

## 1. 项目结构

```text
CSJKtest
├── api                     # 接口地址管理
├── common                  # 公共方法
├── config                  # 配置文件
├── data                    # 测试数据
├── ci                      # 持续集成示例
├── docs                    # 文档说明
├── reports                 # 测试报告输出目录
├── testcases               # 测试用例
├── conftest.py             # pytest 全局夹具
├── pytest.ini              # pytest 配置
├── requirements.txt        # 依赖文件
└── README.md               # 项目总说明
```

## 2. 快速开始

### 2.1 安装依赖

```bash
pip install -r requirements.txt
```

### 2.2 执行全部用例

```bash
pytest
```

### 2.3 执行登录用例

```bash
pytest -m login
```

### 2.4 生成 Allure 报告

先确认本机已安装 Allure 命令行工具，然后执行：

```bash
allure serve reports/allure-results
```

或者生成静态报告：

```bash
allure generate reports/allure-results -o reports/allure-report --clean
```

## 3. 环境切换

默认执行 `uat` 环境，也可以指定环境：

```bash
pytest --env=uat
```

环境配置文件在 [config/env/uat.yaml](/Users/xueguanglai/Desktop/work/CSJKtest/config/env/uat.yaml)。

## 4. 示例说明

项目已内置一个登录接口示例，并补了电商模块模板：

- 接口：`juranApp/login`
- 请求方式：`POST`
- 请求体：JSON

示例用例位置：

- [test_login.py](/Users/xueguanglai/Desktop/work/CSJKtest/testcases/test_login.py)
- [login_case.yaml](/Users/xueguanglai/Desktop/work/CSJKtest/data/login/login_case.yaml)
- [test_product.py](/Users/xueguanglai/Desktop/work/CSJKtest/testcases/test_product.py)
- [test_cart.py](/Users/xueguanglai/Desktop/work/CSJKtest/testcases/test_cart.py)
- [test_order.py](/Users/xueguanglai/Desktop/work/CSJKtest/testcases/test_order.py)
- [test_refund.py](/Users/xueguanglai/Desktop/work/CSJKtest/testcases/test_refund.py)

## 5. 当前增强版能力

- 支持登录后自动提取 `token`
- 支持自动把 `token` 放到请求头
- 支持响应字段提取到上下文
- 支持 `{{变量}}` 占位符替换
- 支持商品、购物车、订单模块模板
- 支持 Jenkins 持续集成示例

## 6. 基于登录接口做后续业务

后续业务接口测试，推荐按角色复用登录夹具。

例如：

```python
def test_order_list(http_client, order_login_token):
    response = http_client.send(
        method="post",
        url="/api/order/list",
        json={"pageNum": 1, "pageSize": 10},
    )
    assert response.status_code == 200
```

说明：

- `order_login_token`、`product_login_token`、`refund_login_token` 分别对应不同业务账号
- 账号配置统一在 [account.yaml](/Users/xueguanglai/Desktop/work/CSJKtest/data/account/account.yaml)
- 登录成功后自动提取 `jwtToken`
- 后续请求会自动把 `jwtToken` 带到请求头
- 这样不同业务模块可以绑定不同账号，不会互相影响

## 7. 文档入口

- [操作文档](/Users/xueguanglai/Desktop/work/CSJKtest/docs/01_操作文档.md)
- [扩展文档](/Users/xueguanglai/Desktop/work/CSJKtest/docs/02_扩展文档.md)
- [知识库说明](/Users/xueguanglai/Desktop/work/CSJKtest/docs/03_知识库说明.md)
- [团队维护规范](/Users/xueguanglai/Desktop/work/CSJKtest/docs/04_团队维护规范.md)
- [新增业务模块标准流程](/Users/xueguanglai/Desktop/work/CSJKtest/docs/05_新增业务模块标准流程.md)
- [接口返回结构约定](/Users/xueguanglai/Desktop/work/CSJKtest/docs/06_接口返回结构约定.md)
- [常见问题排查手册](/Users/xueguanglai/Desktop/work/CSJKtest/docs/07_常见问题排查手册.md)
- [团队协作边界说明](/Users/xueguanglai/Desktop/work/CSJKtest/docs/08_团队协作边界说明.md)
