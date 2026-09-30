import sys
import operator 

OPS = { 
    '+': operator.add, 
    '-': operator.sub,
    '*': operator.mul,
}

TERMINALS = ['x', 'y', '0', '1', '2']


if len(sys.argv) < 2:
    print("Error: Please provide a filename.")
    print("Usage: python program.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

try:
    examples = []
    with open(filename, 'r') as file:
        for line in file: 
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = [int(val.strip()) for val in line.split(',')]
            x, y, target = parts[0], parts[1], parts[2]
            examples.append((x, y, target))
except FileNotFoundError:
    print(f"Error: File '{filename}' not found.")
    sys.exit(1)


def eval_terminal(token: str, x: int, y: int) -> int:
    if token == 'x':
        return x
    elif token == 'y':
        return y
    else:
        return int(token)
    
def synthesize(examples, max_size=15):
    target_outputs = tuple(target for _, _, target in examples)
    expressions_by_size = {}
    seen_outputs = set()

    expressions_by_size[1] = []
    for term in TERMINALS:
        outputs = tuple(eval_terminal(term, x, y) for x, y, _ in examples)
        if outputs not in seen_outputs:
            seen_outputs.add(outputs)
            expressions_by_size[1].append((term, outputs))
        if outputs == target_outputs:
            return term
    
    for s in range(3, max_size + 1, 2):
        expressions_by_size[s] = []
        for s1 in range(1, s - 1, 2):
            s2 = s - 1 - s1
            if s2 not in expressions_by_size:
                continue

            for op_symbol, op_fn in OPS.items():
                for expr1, outputs1 in expressions_by_size[s1]:
                    for expr2, outputs2 in expressions_by_size[s2]:
                        new_expr = f"{op_symbol} {expr1} {expr2}"
                        new_outputs = tuple(op_fn(o1, o2) for o1, o2 in zip(outputs1, outputs2))

                        if new_outputs not in seen_outputs:
                            seen_outputs.add(new_outputs)
                            expressions_by_size[s].append((new_expr, new_outputs))

                        if new_outputs == target_outputs:
                            return new_expr
                        
    return None

if __name__ == '__main__':
    result = synthesize(examples)
    if result:
        print(f"Synthesized expression: {result}")
    else:
        print("No expression found that matches the examples.")