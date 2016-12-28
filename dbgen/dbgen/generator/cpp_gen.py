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
        self.table_name = ""
        self.fields = {} # 存储字段列表 field=>type

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
        if "objectName" not in root.attrib:
            print "<object> section has no attribute: objectName"
            return False
        self.table_name = root.attrib["tableName"]
        obj_prefix = root.attrib["objectName"]
        filename_prefix = self.table_name.lower()
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
        elif typename == "int":
            return "int"
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
            self.fields[elem.attrib["name"]] = elem.attrib["type"] # 将字段名称储存, 构建sql语句使需要
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

    def _get_param_type(self, typename):
        """
        获取接口的参数类型
        """
        if typename == "string":
            return "const std::string&"
        elif typename == "int":
            return "int"
        else:
            return "{0}_t".format(typename)

    def _get_dao_struct(self, prefix):
        """
        生成ObjectDAO结构
        """
        struct = "struct {0}DAO : public BaseDAO".format(prefix)
        struct += " { \n"
        struct += "  virtual ~{0}DAO() = default; \n\n".format(prefix)
        struct += "  static {0}DAO& GetInstance(); \n\n".format(prefix)

        # 生成 get 接口
        for query in self.tree.iter(tag="get"):
            interface = "  virtual int {0}(".format(query.attrib['name'])
            # 构建输入参数
            for param in query.iter(tag="param"):
                interface += "{0} {1},".format(
                    self._get_param_type(param.attrib['type']),
                    param.attrib['name'])
            interface = interface[:len(interface) - 1]
            # 构建返回参数
            for result in query.iter(tag="result"):
                interface += ", {0}& {1},".format(
                    result.attrib['type'],
                    result.attrib['name'])
            interface = interface[:len(interface) - 1]
            interface += ") = 0;\n\n"

            # 添加到string
            struct += interface

        # 生成 create 接口
        for query in self.tree.iter(tag="create"):
            interface = "  virtual {0} {1}(".format(
                self._get_type(query.attrib['returnType']),
                query.attrib['name'])
            for param in query.iter(tag="param"):
                interface += "{0}& {1},".format(
                    param.attrib['type'],
                    param.attrib['name']
                )
            interface = interface[:len(interface) - 1]
            interface += ") = 0;\n\n"

            # 添加到string
            struct += interface

        # 生成list接口
        for query in self.tree.iter(tag="list"):
            interface = "  virtual int {0}(".format(query.attrib['name'])

            # 查询参数
            for param in query.iter(tag="condition"):
                interface += "{0} {1}, ".format(
                    self._get_param_type(param.attrib['type']),
                    param.attrib['name']
                )

            # 返回结果
            interface += "{0}DOList& {1}".format(prefix, query.attrib['resultName'])
            interface += ") = 0;\n\n"

            # 添加到string
            struct += interface

        #TODO: 生成update接口
        #TODO: 生成insert接口
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
        struct += "  virtual ~{0}DAOImpl() = default; \n\n".format(obj_prefix)

        # 生成 get 接口
        for query in self.tree.iter(tag="get"):
            interface = "  int {0}(".format(query.attrib['name'])
            # 构建输入参数
            for param in query.iter(tag="param"):
                interface += "{0} {1},".format(
                    self._get_param_type(param.attrib['type']),
                    param.attrib['name'])
            interface = interface[:len(interface) - 1]
            # 构建返回参数
            for result in query.iter(tag="result"):
                interface += ", {0}& {1},".format(
                    result.attrib['type'],
                    result.attrib['name'])
            interface = interface[:len(interface) - 1]
            interface += ") override;\n\n"

            # 添加到string
            struct += interface

        # 生成 create 接口
        for query in self.tree.iter(tag="create"):
            interface = "  {0} {1}(".format(
                self._get_type(query.attrib['returnType']),
                query.attrib['name'])
            for param in query.iter(tag="param"):
                interface += "{0}& {1},".format(
                    param.attrib['type'],
                    param.attrib['name']
                )
            interface = interface[:len(interface) - 1]
            interface += ") override;\n\n"

            # 添加到string
            struct += interface

        # 生成list接口
        for query in self.tree.iter(tag="list"):
            interface = "  int {0}(".format(query.attrib['name'])

            # 查询参数
            for param in query.iter(tag="condition"):
                interface += "{0} {1}, ".format(
                    self._get_param_type(param.attrib['type']),
                    param.attrib['name']
                )

            # 返回结果
            interface += "{0}DOList& {1}".format(obj_prefix, query.attrib['resultName'])
            interface += ") override;\n\n"

            # 添加到string
            struct += interface

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

        # 生成 get 接口
        for query in self.tree.iter(tag="get"):
            interface = "int {0}DAOImpl::{1}(".format(obj_prefix, query.attrib['name'])
            # 构建输入参数
            for param in query.iter(tag="param"):
                interface += "{0} {1},".format(
                    self._get_param_type(param.attrib['type']),
                    param.attrib['name'])
            interface = interface[:len(interface) - 1]
            # 构建返回参数
            for result in query.iter(tag="result"):
                interface += ", {0}& {1},".format(
                    result.attrib['type'],
                    result.attrib['name'])
            interface = interface[:len(interface) - 1]
            interface += ") {\n"

            # 生成实现代码
            interface += "  return DoStorageQuery(\"{0}\",\n".format(query.attrib['connPool'])
            interface += "  \t\t\t[&](std::string& query_string) {\n"
            interface += "  \t\t\t  folly::format(&query_string,\n"

            keys = ""
            for key in self.fields.iterkeys():
                keys += "{0},".format(key)
            keys = keys[:len(keys) - 1]
            interface += "  \t\t\t  \t\t\"SELECT {0} FROM {1} WHERE \"\n".format(
                keys,
                self.table_name)

            interface += "  \t\t\t  \t\t\""
            for param in query.iter(tag="param"):
                interface += param.attrib['name'] + "="
                if param.attrib['type'] == "string":
                    interface += "'{}' AND "
                else:
                    interface += "{} AND "
            interface = interface[:len(interface) - 5]
            interface += "\",\n"
            for param in query.iter(tag="param"):
                interface += "  \t\t\t  \t\t{0},\n".format(param.attrib['name'])
            interface = interface[:len(interface) - 2]
            interface += ");\n"
            interface += "  \t\t\t},\n"
            interface += "  \t\t\t[&](db::QueryAnswer& answ) -> int {\n"
            interface += "  \t\t\t  int result = CONTINUE;\n\n"
            interface += "  \t\t\t  do {\n"

            for result in query.iter(tag="result"):
                name = result.attrib['name']
                i = 0
                for key, value in self.fields.iteritems():
                    if value == "string":
                        interface += "  \t\t\t  \tDB_GET_COLUMN({0}, {1}.{2});\n".format(
                            i, name, key)
                    else:
                        interface += "  \t\t\t  \tDB_GET_RETURN_COLUMN({0}, {1}.{2});\n".format(
                            i, name, key)
                    i = i+1

            interface += "  \t\t\t  } while (0);\n\n"
            interface += "  \t\t\t  return BREAK;\n"
            interface += "  \t\t\t});\n"

            # 添加到string
            interface += "}\n\n"
            struct += interface

        # 生成 create 接口实现
        for query in self.tree.iter(tag="create"):
            interface = "{0} {1}DAOImpl::{2}(".format(
                self._get_type(query.attrib['returnType']),
                obj_prefix,
                query.attrib['name'])

            # 构建参数
            param_name = ""
            for param in query.iter(tag="param"):
                param_name = param.attrib['name']
                interface += "{0}& {1}, ".format(param.attrib['type'], param.attrib['name'])
            interface = interface[:len(interface) - 2] + ") {\n"
            interface += "  return DoStorageInsertID(\"{0}\",\n".format(query.attrib['connPool'])

            interface += "  \t\t\t[&](std::string& query_string) {\n"
            interface += "  \t\t\t  db::QueryParam p;\n"

            # 构建字段值
            for key, value in self.fields.iteritems():
                if key == "status":
                    continue
                if value == "string":
                    interface += "  \t\t\t  p.AddParam({0}.{1}.c_str());\n".format(
                        param_name,
                        key)
                else:
                    interface += "  \t\t\t  p.AddParam(&{0}.{1});\n".format(
                        param_name,
                        key)
            interface += "\n"
            interface += "  \t\t\t  db::MakeQueryString(\"INSERT INTO {0}\"\n".format(
                self.table_name)
            key_str = "\"("
            holds_str = "\"("
            i = 1
            for key in self.fields.iterkeys():
                key_str += "{0},".format(key)
                if key == "status":
                    holds_str += "1,"
                    continue
                holds_str += ":{0},".format(i)
                i = i + 1
            key_str = key_str[:len(key_str) - 1] + ")\""
            holds_str = holds_str[:len(holds_str) - 1] + ")\""
            interface += "  \t\t\t  \t\t{0}\n".format(key_str)
            interface += "  \t\t\t  \t\t\" VALUES \"\n"
            interface += "  \t\t\t  \t\t{0},\n".format(holds_str)
            interface += "  \t\t\t  \t\t&p,\n"
            interface += "  \t\t\t  \t\t&query_string);\n"

            interface += "  \t\t\t});\n"
            interface += "}\n\n"

            struct += interface

        # 生成 list 接口实现
        for query in self.tree.iter(tag="list"):
            interface = "int {0}DAOImpl::{1}(".format(
                obj_prefix,
                query.attrib['name'])
            # 构建参数列表
            for condition in query.iter(tag="condition"):
                interface += "{0} {1}, ".format(
                    self._get_param_type(condition.attrib['type']),
                    condition.attrib['name'])
            # 输出参数
            interface += "{0}DOList& {1})".format(
                obj_prefix,
                query.attrib['resultName'])
            interface += " {\n"

            interface += "  return DoStorageQuery(\"{0}\",\n".format(query.attrib['connPool'])
            interface += "  \t\t\t[&](std::string& query_string) {\n"
            interface += "  \t\t\t  query_string = folly::sformat("
            keys = ""
            for key in self.fields.iterkeys():
                keys += "{0},".format(key)
            keys = keys[:len(keys) - 1]
            interface += "\"SELECT {0} FROM {1} WHERE ".format(keys, self.table_name)
            for condition in query.iter(tag="condition"):
                value = "{}"
                if condition.attrib['type'] == "string":
                    value = "'{}'"
                interface += "{0}{1}{2} AND ".format(
                    condition.attrib['name'],
                    condition.attrib['method'],
                    value)
            interface = interface[:len(interface) - 5]
            interface += " LIMIT {0}".format(query.attrib['limit'])
            if "offset" in query.attrib:
                interface += " OFFSET {0}".format(query.attrib['offset'])
            interface += "\",\n"
            for condition in query.iter(tag="condition"):
                interface += "  \t\t\t  \t\t" + condition.attrib['name'] + ",\n"
            interface = interface[:len(interface) - 2] + ");\n"
            interface += "  \t\t\t},\n"

            interface += "  \t\t\t[&](db::QueryAnswer& answ) -> int {\n"
            interface += "  \t\t\t  auto data = std::make_shared<{0}DO>();\n".format(obj_prefix)

            i = 0
            for key, value in self.fields.iteritems():
                interface += "  \t\t\t  answ.GetColumn({0}, &data.{1});\n".format(i, key)
                i = i+1
            interface += "  \t\t\t  {0}.push_back(data);\n".format(
                query.attrib['resultName']
            )
            interface += "  \t\t\t  return CONTINUE;\n"
            interface += "  \t\t\t});\n"

            interface += "}\n\n"
            # 添加到string
            struct += interface

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
