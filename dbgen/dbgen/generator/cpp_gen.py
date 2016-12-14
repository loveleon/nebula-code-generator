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

    def __init__(self, tree):
        """
        以xml tree初始化
        """
        if not tree:
            raise Exception("tree is empty!!")
        self.tree = tree
        self.output_dir = None

    def generate(self, output_dir):
        """
        开始生成代码
        """
        if not output_dir:
            print "output dir is not empty!"
            return False
        self.output_dir = output_dir

        if not self.tree:
            print "xml tree is empty!!"
            return False

        # 检测目录是否存在，若不存在，则建立目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        root = self.tree.getroot()
        if "tableName" not in root.attrib:
            print "<object> section has no attribute: tableName"
            return False
        obj_prefix = root.attrib["tableName"]
        filename_prefix = obj_prefix.lower()
        # 生成 _do 文件
        if not self._generate_do(obj_prefix, filename_prefix):
            return False

        # 生成 _dao 文件
        if not self._generate_dao(obj_prefix, filename_prefix):
            return False

        # 生成 _impl 文件
        if not self._generate_dao_impl(obj_prefix, filename_prefix):
            return False

        return True

    def _get_type(self, typename):
        """
        获取type映射的名称
        """
        if typename == "string":
            return "std::{0}".format(typename)
        else:
            return "{0}_t".format(typename)

    def _get_copyright(self):
        """
        获取版权信息
        """
        cpright = "/* \n"
        cpright += " *  Copyright (c) 2016, https://github.com/nebula-im/imengine \n"
        cpright += " *  All rights reserved. \n"
        cpright += " * \n"
        cpright += " * Licensed under the Apache License, Version 2.0 (the \"License\"); \n"
        cpright += " * you may not use this file except in compliance with the License. \n"
        cpright += " * You may obtain a copy of the License at \n"
        cpright += " * \n"
        cpright += " *   http://www.apache.org/licenses/LICENSE-2.0 \n"
        cpright += " * \n"
        cpright += " * Unless required by applicable law or agreed to in writing, software \n"
        cpright += " * distributed under the License is distributed on an \"AS IS\" BASIS, \n"
        cpright += " * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n"
        cpright += " * See the License for the specific language governing permissions and \n"
        cpright += " * limitations under the License. \n"
        cpright += "  */ \n\n"
        return cpright

    def _get_redefine_header(self, header_line):
        """
        获取预编译头，文件避免重复引入的头
        """
        header = ""
        header += "#ifndef " + header_line.upper() + " \n"
        header += "#define " + header_line.upper() + " \n\n"
        return header

    def _get_redefine_tail(self, tail_line):
        """
        获取预编译尾，与header遥相呼应
        """
        return "#endif//{0} \n".format(tail_line.upper())

    def _get_do_struct(self, prefix):
        """
        生成objectDO结构信息
        """
        struct = "struct {0}DO {1} \n".format(prefix, "{")
        root = self.tree.getroot()

        meta = "  META("
        for elem in root[0].getiterator("field"):
            meta += "{0}, ".format(elem.attrib["name"]) # 构建meta
            # 生成字段
            field = "  %s %s" % (self._get_type(elem.attrib["type"]), elem.attrib["name"])
            if "defaultValue" in elem.attrib:
                field += "{%s}" % (elem.attrib["defaultValue"])
            struct += field + ";\n"
        struct += "\n"

        meta = meta[0:len(meta) - 2] + "); \n"
        struct += meta
        struct += "};\n\n"
        return struct

    def _generate_do(self, obj_prefix, filename_prefix):
        """
        生成object_do.h文件
        """
        filename = "{0}_do.h".format(filename_prefix)
        print "writting {0} to {1}".format(filename, self.output_dir)
        with open(self.output_dir + "/" + filename, 'w') as fin:
            # 写入版权信息
            fin.write(self._get_copyright())
            # 写入ifdef信息
            line = "IMENGINE_DAL_{0}_DO_H_".format(obj_prefix.upper())
            fin.write(self._get_redefine_header(line))

            # 写入include信息
            fin.write("#include <list> \n")
            fin.write("#include <string> \n\n")
            fin.write("#include \"dal/base_dal.h\" \n\n")

            # 写入objectDO结构信息
            fin.write(self._get_do_struct(obj_prefix))

            # 写入ptr, list定义
            fin.write("using {0}DOPtr = std::shared_ptr<{0}DO>; \n".format(obj_prefix))
            fin.write("using {0}DOList = std::list<{0}DOPtr>; \n\n".format(obj_prefix))

            # 写入endif//
            fin.write(self._get_redefine_tail(line))

            # 关闭文件
            fin.close()

        return True

    def _get_dao_struct(self, prefix):
        """
        生成ObjectDAO结构
        """
        struct = "struct {0}DAO : public BaseDAO".format(prefix)
        struct += " { \n"
        struct += "  virtual ~{0}DAO() = default; \n\n".format(prefix)
        struct += "  static {0}DAO& GetInstance(); \n\n".format(prefix)
        #TODO: 生成纯虚接口函数
        struct += "};\n\n"
        return struct

    def _generate_dao(self, obj_prefix, filename_prefix):
        """
        生成object_dao.h文件
        """
        filename = "{0}_dao.h".format(filename_prefix)
        print "writting {0} to {1}".format(filename, self.output_dir)
        with open(self.output_dir + "/" + filename, 'w') as fin:

            # 写入版权信息
            fin.write(self._get_copyright())
            # 写入ifdef信息
            line = "IMENGINE_DAL_{0}_DAO_H_".format(obj_prefix.upper())
            fin.write(self._get_redefine_header(line))

            # 写入include信息
            fin.write("#include \"dal/{0}_do.h\"\n\n".format(obj_prefix.lower()))

            # 写入struct信息
            fin.write(self._get_dao_struct(obj_prefix))

            # 写入endif//
            fin.write(self._get_redefine_tail(line))

            # 关闭文件
            fin.close()

        return True

    def _generate_dao_impl(self, obj_prefix, filename_prefix):
        """
        生成object_dao_impl.h, object_dao_impl.cc文件
        """
        if not self._generate_dao_impl_h(obj_prefix, filename_prefix):
            return False

        if not self._generate_dao_impl_cc(obj_prefix, filename_prefix):
            return False
        return True

    def _get_dao_impl_struct(self, obj_prefix):
        """
        生成ObjectDAOImpl结构
        """
        struct = "struct {0}DAOImpl : public {0}DAO".format(obj_prefix)
        struct += " { \n"
        struct += " virtual ~{0}DAOImpl() = default; \n\n".format(obj_prefix)
        #TODO: 生成接口实现函数
        struct += "}; \n\n"
        return struct

    def _generate_dao_impl_h(self, obj_prefix, filename_prefix):
        """
        生成object_dao_impl.h
        """
        filename = "{0}_dao_impl.h".format(filename_prefix)
        print "writting {0} to {1}".format(filename, self.output_dir)
        with open(self.output_dir + "/" + filename, 'w') as fin:
            # 写入版权信息
            fin.write(self._get_copyright())
            # 写入ifdef信息
            line = "IMENGINE_DAL_{0}_DAO_IMPL_H_".format(obj_prefix.upper())
            fin.write(self._get_redefine_header(line))

            # 写入include信息
            fin.write("#include \"dal/{0}_dao.h\"\n\n".format(obj_prefix.lower()))

            # 写入struct信息
            fin.write(self._get_dao_impl_struct(obj_prefix))

            # 写入endif//
            fin.write(self._get_redefine_tail(line))

            # 关闭文件
            fin.close()

        return True

    def _get_dao_impl_funcs(self, obj_prefix):
        """
        生成函数实现代码
        """
        struct = "{0}DAO& {0}DAO::GetInstance()".format(obj_prefix)
        struct += " {\n"
        struct += "  static {0}DAOImpl impl;\n".format(obj_prefix)
        struct += "  return impl;\n"
        struct += "}\n\n"
        #TODO: 生成实现函数
        return struct

    def _generate_dao_impl_cc(self, obj_prefix, filename_prefix):
        """
        生成object_dao_impl.cc文件
        """
        filename = "{0}_dao_impl.cc".format(filename_prefix)
        print "writting {0} to {1}".format(filename, self.output_dir)
        with open(self.output_dir + "/" + filename, 'w') as fin:
            # 写入版权信息
            fin.write(self._get_copyright())

            # 写入include信息
            fin.write("#include \"dal/{0}_dao_impl.h\"\n\n".format(obj_prefix.lower()))

            # 写入struct信息
            fin.write(self._get_dao_impl_funcs(obj_prefix))

            # 关闭文件
            fin.close()

        return True
