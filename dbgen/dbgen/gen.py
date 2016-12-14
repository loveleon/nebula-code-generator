# -*- coding: utf-8 -*-
# file: gen.py
"""
入口文件
"""
import argparse
from parser.xml_parser import XmlParser
from generator.cpp_gen import CppGenerator

# 定义命令行参数解析规则
parser = argparse.ArgumentParser(description="Data Access Layer Generator Usage")
parser.add_argument("-i", "--input", dest="src", help="input the defination filename")
parser.add_argument("-o", "--output", dest="dest", help="output the generated file")
parser.parse_args()

if __name__ == "__main__":
    # 解析命令行参数
    args = parser.parse_args()
    input_filename = args.src
    output_dir = args.dest
    print "start generating file:{0} to dir: {1}".format(input_filename, output_dir)

    # 解析*.xml内容到内存
    xml_parser = XmlParser()
    if not xml_parser.load(input_filename):
        print "reading error from file:{0}".format(input_filename)
        exit(-1)

    # 生成文件
    cpp_generator = CppGenerator(xml_parser.tree)
    if not cpp_generator.generate(output_dir):
        print "generate cpp code from:{0} failed".format(input_filename)
        exit(-1)

    # 输出生成结果
    print "generate code from {0} successfully!".format(input_filename)
