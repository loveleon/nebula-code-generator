# -*- coding: utf-8 -*-
# file: gen.py
"""
生成.h,.cc 文件
"""
import os

class CppGenerator(object):
    """
    生成*.h, *.cc文件
    """
    tree = None

    def __init__(self, tree):
        """
        以xml tree初始化
        """
        if not tree:
            raise Exception("tree is empty!!")
        self.tree = tree

    def generate(self, output_dir):
        """
        开始生成代码
        """
        if not output_dir:
            print "output dir is not empty!"
            return False

        # 检测目录是否存在，若不存在，则建立目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 生成 header
        self._generate_header()

        # 生成 cc
        self._generate_cc()
        return True

    def _generate_header(self):
        """
        生成头文件
        """

    def _generate_cc(self):
        """
        生成cc文件
        """
