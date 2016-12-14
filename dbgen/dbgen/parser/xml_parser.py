# -*- coding: utf-8 -*-
# file: gen.py
"""
解析xml模板
"""
import xml.etree.ElementTree as ElementTree

class XmlParser(object):
    """
    读取xml文件，并且解析内容
    """
    tree = None

    def load(self, filename):
        """
        filename: xml filename
        """
        if not filename:
            print "empty filename"
            return False

        # 解析成xml tree
        try:
            self.tree = ElementTree.parse(filename)
        except xml.etree.ElementTree.ParseError as error:
            print "parse {0} error: {1}".format(filename, error)
        return True
