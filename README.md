# 接口自动化测试框架

基于 `pytest + requests + allure` 的数据驱动接口自动化框架：用例写在 YAML 里，测试文件只是薄壳。

## 1. 项目结构

```text
CSJKtest
├── common/                 # 公共层：请求、登录、断言、提取、占位符、报告、通知
├── config/
│   ├── project.yaml        # 项目级配置：默认环境、超时、业务码字段、钉钉
│   └── env/<env>.yaml      # 环境配置：base_url、默认请求头、登录接口
├── data/
│   ├── account/<env>.yaml  # 各环境的角色账号
│   └── <模块>/<模块>_case.yaml  # 用例数据
├── testcases/test_<模块>.py # 测试文件
├── run.py                  # 统一执行入口
├── conftest.py             # 夹具、自定义 HTML 报告、钉钉通知
├── ci/Jenkinsfile
└── docs/                   # 文档
```

## 2. 快速开始

统一入口是 `run.py`，用系统的 `python3` 直接执行即可。首次执行会自动创建虚拟环境 `.venv` 并安装依赖，之后只在 `requirements.txt` 有变化时重新安装。

```bash
python3 run.py                      # 默认环境的全部用例
python3 run.py login pay_product    # 只跑指定模块（testcases/test_<模块>.py）
python3 run.py -m smoke             # 只跑冒烟用例
python3 run.py --env=uat            # 指定环境（对应 config/env/<env>.yaml）
```

参数原样传给 pytest。不传 `--env` 时使用 `config/project.yaml` 里的 `default_env`（当前是 `uat`）。

## 3. 报告

- 自定义 HTML 报告：每次执行后生成在 `reports/<时间>_<模块>.html`，包含每条用例的请求和响应。
- 报告清理：`reports/` 下只保留最新 3 份 HTML 报告（`config/project.yaml` 的 `report_keep_count`），Allure 原始结果每次执行前清空，只保留最近一次。
- Allure：`allure serve reports/allure-results`。
- 钉钉：每次执行完发送汇总，配置在 `config/project.yaml`；把 `dingtalk_notify_on_success` 改成 `false` 则只在有失败或异常用例时发送。

## 4. 服务器部署

把项目目录放到服务器上，Jenkins 构建步骤（执行 shell）写：

```bash
#!/bin/bash
cd /usr/xgl_work/CSJKtest
python3 run.py
```

用例有失败时退出码非 0，Jenkins 会把构建标记为失败。

可选：想让钉钉通知里的报告变成可点击链接，需要把 `reports/` 目录以 HTTP 方式暴露出来（`./serve_reports.sh 8088` 或 Nginx），并设置环境变量 `REPORT_BASE_URL`（或 `config/project.yaml` 的 `report_base_url`）为访问地址前缀。不设置则显示本地路径。

## 5. 当前接入的环境

- UAT：`https://gatewayuat.wolaicaipay.com`，配置在 `config/env/uat.yaml`。
- 登录角色 `manage_user`（运营管理端），账号在 `data/account/uat.yaml`。
- 登录态通过 Cookie 中的 `eh_uatJwtToken` 携带，框架自动处理。
- 新增业务模块见 [新增模块流程](docs/02_新增模块流程.md)；新增环境就加一份 `config/env/<env>.yaml` 和 `data/account/<env>.yaml`。

## 6. 文档

- [用例 YAML 字段说明](docs/01_用例YAML字段说明.md)
- [新增模块流程](docs/02_新增模块流程.md)
- [常见问题排查](docs/03_常见问题排查.md)
