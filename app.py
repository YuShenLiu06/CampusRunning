#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校园跑步数据生成器 - Web应用入口

作者: 猫娘幽浮喵
"""

import logging
import sys

try:
    from flask import Flask
except ImportError:
    print("错误: Flask 未安装。请运行: pip install flask")
    sys.exit(1)

from web.routes import create_app


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    app = create_app()

    print("=" * 50)
    print("校园跑步数据生成器 - Web界面")
    print("访问 http://127.0.0.1:5000")
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)

    app.run(debug=True, host="127.0.0.1", port=5000)


if __name__ == "__main__":
    main()
