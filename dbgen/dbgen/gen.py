# -*- coding: utf-8 -*-
# file: gen.py
"""
入口文件
"""
import argparse
from parser.xml_parser import XmlParser
from generator.cpp_gen import CppGenerator

def read_args():
    """
    定义命令行参数
    """
    parser = argparse.ArgumentParser(description="Data Access Layer Generator Usage")
    parser.add_argument("-i", "--input", dest="src", help="input the defination filename")
    parser.add_argument("-o", "--output", dest="dest", help="output the generated file")

    args = parser.parse_args()
    return args.src, args.dest

def do_main():
    """
    执行main函数
    """
    input_filename, output_dir = read_args()
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

if __name__ == "__main__":
    do_main()
