from exptree import ExpNode, ExpressionState
class EquivalentExpressions:
    def __init__(self, old: ExpNode, new: ExpNode, custom_name=None):
        self.old = old
        self.new = new
        self.custom_name = custom_name

    def expression_replace(self, expression: ExpressionState) -> list[ExpressionState]:
        occurrences = expression.root.find_all(lambda x: x.starts_with(self.old))
        new_expressions = []
        for occ in occurrences:
            new_expressions.append(expression.replace(occ, self.new, extra_children=occ.children[len(self.old.children):]))
        return new_expressions


    def __str__(self):
        return f"def {self.old} > {self.new}" if self.custom_name is None else self.custom_name

    def __repr__(self):
        return str(self)
    

def test_equivalent_expressions():
    original_expression = ExpressionState.from_string("a b c (a b c) (a b c d) (a b c d e)", "c1")
    equivalent_expressions = [
        EquivalentExpressions(ExpNode.from_string("a b c"), ExpNode.from_string("a (b c)")),
        EquivalentExpressions(ExpNode.from_string("a b c"), ExpNode.from_string("c b a"))
    ]
    for equivalent_expression in equivalent_expressions:
        print(equivalent_expression)
        for new_expression in equivalent_expression.expression_replace(original_expression):
            print(new_expression)


if __name__ == "__main__":
    test_equivalent_expressions()