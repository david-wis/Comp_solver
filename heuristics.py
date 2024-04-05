def by_length(node):
    return abs(node.state.exp.count(' ') - node.state.expec_exp.count(' '))


def weight(expression):
    terms = expression.replace('(', '').replace(')', '').split(' ')
    w = 0
    for term in terms:
        if term.startswith('c'):
            w += int(term[1:])
    return w

def by_constant_weight(node):
    return abs(weight(node.state.exp) - weight(node.state.expec_exp)) + node.state.exp.count("f")