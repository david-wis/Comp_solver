def get_token(expression, start_index):
    current_index = start_index
    if expression[current_index] == ' ': raise ValueError("Invalid expression")
    if expression[current_index] == '(':
        scope_count = 1
        while scope_count > 0 and current_index < len(expression):
            current_index += 1
            scope_count += (expression[current_index] == '(') - (expression[current_index] == ')')
        if scope_count != 0:
            raise ValueError("Invalid parenthesis")
        current_index += 1        
    else:
        while current_index < len(expression) and expression[current_index] != ')' and expression[current_index] != ' ':
            current_index += 1
    return expression[start_index:current_index], start_index, current_index

def get_subexpressions(expression):
    subexpressions = []
    if expression[0] == '(':
        index = 1
        while index < len(expression):
            se, start, end = get_token(expression, index)
            subexpressions.append(se)
            index = end + 1
    return subexpressions

def get_all_subexpressions(expression):
    subexpressions = []
    index = 0
    while index < len(expression):
        if index == 0 or expression[index] == '(' or expression[index - 1] == ' ' or expression[index - 1] == '(':
            token, start, end = get_token(expression, index)
            subexpressions.append(token)
        index += 1
        
    return subexpressions

def get_parameters_subexpressions(expression):
    subexpressions = []
    index = 0
    while index < len(expression):
        se, _, end = get_token(expression, index)
        subexpressions.append(se)
        index = end + 1
    return subexpressions

def normalize_expression(expression):
    while expression.startswith("("):
        _, _, end = get_token(expression, 0)
        expression = expression[1:end - 1] + expression[end:]
    index = expression.find("((")
    while (index := expression.find("((", index)) != -1:
        _, _, end = get_token(expression, index + 1)
        expression = expression[:index] + expression[index+1:end-1]+ expression[end:]
    return expression

def binarize_expression(expression):
    if expression.startswith("(") and expression.endswith(")"):
        expression = expression[1:-1]
    current_anchor , _, end = get_token(expression, 0)
    while end < len(expression): 
        if expression[end] == ' ':
            parameter, _, end = get_token(expression, end + 1)
            expression = f"({current_anchor} {binarize_expression(parameter)})" + expression[end:]
            current_anchor , _, end = get_token(expression, 0)
        else:
            raise ValueError("Invalid expression")
    return expression

def index_of_pointer(list, pointer):
    index = 0
    while index < len(list):
        if pointer is list[index]: break
        index += 1
    return index if index < len(list) else -1


if __name__ == "__main__":
    
    #normalize expression
    assert (normalize_expression("a b") == "a b"), f"Got: {normalize_expression('a b')}"
    assert (normalize_expression("(a b)") == "a b"), f"Got: {normalize_expression('(a b)')}"
    assert (normalize_expression("((a b) c)") == "a b c"), f"Got: {normalize_expression('((a b) c)')}"
    assert (normalize_expression("((a b) (c d))") == "a b (c d)"), f"Got: {normalize_expression('((a b) (c d))')}"
    assert (normalize_expression("a (b c)") == "a (b c)"), f"Got: {normalize_expression('a (b c)')}"
    assert (normalize_expression("(((((a b) c) d) e) f) h") == "a b c d e f h"), f"Got: {normalize_expression('(((((a b) c) d) e) f) h')}"
    assert (normalize_expression("a (b (c (d (e f))))") == "a (b (c (d (e f))))"), f"Got: {normalize_expression('a (b (c (d (e f))))')}"
    assert (normalize_expression("a (b c) (d e) (e f)") == "a (b c) (d e) (e f)"), f"Got: {normalize_expression('a (b c) (d e) (e f)')}"
    assert (normalize_expression("a ((b c) d) ((e f) g) (h (i j))") == "a (b c d) (e f g) (h (i j))"), f"Got: {normalize_expression('a ((b c) d) ((e f) g) (h (i j))')}"
    assert (normalize_expression("a b (c ((d e) f) ((g h) (i j)))") == "a b (c (d e f) (g h (i j)))"), f"Got: {normalize_expression('a b (c ((d e) f) ((g h) (i j)))')}"

    #binarize expression
    assert (binarize_expression("a b") == "(a b)"), f"Got: {binarize_expression('a b')}"
    assert (binarize_expression("a b c") == "((a b) c)"), f"Got: {binarize_expression('a b c')}"
    assert (binarize_expression("a (b c)") == "(a (b c))"), f"Got: {binarize_expression('a b c')}"
    assert (binarize_expression("a b c d") == "(((a b) c) d)"), f"Got: {binarize_expression('a b c d')}"
    assert (binarize_expression("a (b c) d") == "((a (b c)) d)"), f"Got: {binarize_expression('a (b c) d')}"
    assert (binarize_expression("a (b (c d))") == "(a (b (c d)))"), f"Got: {binarize_expression('a (b c) d')}"