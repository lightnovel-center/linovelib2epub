import esprima

class ASTPropertyFinder:
    def __init__(self, js_code):
        self.ast = esprima.parse(js_code)

    def find_expr_property(self, expr_name, object_property_name):
        """在 AST 中查找指定表达式名称并进一步查找指定对象属性"""
        self._find_expr_name(self.ast, expr_name, object_property_name)

    def _find_expr_name(self, node, expr_name, object_property_name):
        """递归查找表达式名称的辅助方法"""
        if isinstance(node, esprima.nodes.Node):
            if node.type == 'Program':
                for statement in node.body:
                    self._find_expr_name(statement, expr_name, object_property_name)
            elif node.type == 'VariableDeclaration':
                for decl in node.declarations:
                    if decl.id.name == expr_name:
                        exprs = decl.init
                        self._find_object_property(exprs, object_property_name)
        elif isinstance(node, list):
            for item in node:
                self._find_expr_name(item, expr_name, object_property_name)

    def _find_object_property(self, expr, object_property_name):
        """在对象表达式中查找指定的对象属性"""
        if isinstance(expr, esprima.nodes.Node):
            if expr.type == 'ObjectExpression':
                for prop in expr.properties:
                    if prop.key.name == object_property_name:
                        value = getattr(prop, 'value', None)
                        final_value = getattr(value, 'value', None)
                        if final_value is not None:
                            print(f"Found '{object_property_name}' with value: {final_value}")
                        else:
                            print(f"Found '{object_property_name}' but value is None or nested")
            elif expr.type in ('CallExpression', 'LogicalExpression', 'MemberExpression'):
                # 递归查找表达式的子节点
                self._find_object_property(expr.left if hasattr(expr, 'left') else expr.callee, object_property_name)
                self._find_object_property(expr.right if hasattr(expr, 'right') else expr.arguments,
                                           object_property_name)
        elif isinstance(expr, list):
            for item in expr:
                self._find_object_property(item, object_property_name)


# 使用示例
# 读取原始 JavaScript 文件
original_js = 'cleaned.js'
with open(original_js, 'r', encoding='utf-8') as file:
    original_code = file.read()

# 初始化 ASTPropertyFinder
finder = ASTPropertyFinder(original_code)

# 查找 ReadTools 对象中的 contentid 字段
finder.find_expr_property('ReadTools', 'contentid')
