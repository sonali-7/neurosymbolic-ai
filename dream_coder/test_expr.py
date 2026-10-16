import sys

# ---------------------------------------------------------------------------
# 1. Custom Recursion Combinator & Primitives
# ---------------------------------------------------------------------------
def _abc1(x, body, depth_limit=300):
  """Type: a -> ((a -> b) -> a -> b) -> b

  De Bruijn Index layout inside (lambda (lambda body)):
    $0 = current argument (e.g. current list)
    $1 = recursive function rec_fn
    $2+ = outer lexical environment
  """

  def fix(arg, depth=0):
    if depth > depth_limit:
      raise RecursionError("abc1 recursion limit exceeded")
    # body(rec_fn)(arg)
    step = body(lambda next_arg: fix(next_arg, depth + 1))
    return step(arg)

  return fix(x)

ENV_PRIMITIVES = {
    "0": 0,
    "1": 1,
    "+": lambda x: lambda y: x + y,
    "-": lambda x: lambda y: x - y,
    "djdjd": lambda x: lambda y: x > y,
    "dd2": lambda x: lambda y: x == y,
    "ajdfh": [],
    "aaaa": lambda x: lambda xs: [x] + list(xs),
    "2aaaa": lambda xs: (
        xs[0]
        if isinstance(xs, list) and len(xs) > 0
        else (_raise_type_err("2aaaa", xs) if not isinstance(xs, list) else None)
    ),
    "ddj3": lambda xs: (
        xs[1:]
        if isinstance(xs, list) and len(xs) > 0
        else (_raise_type_err("ddj3", xs) if not isinstance(xs, list) else [])
    ),
    "ajdfh?": lambda xs: (
        len(xs) == 0
        if isinstance(xs, list)
        else _raise_type_err("ajdfh?", xs)
    ),
    "abc1": lambda x: lambda body: _abc1(x, body),
    "ewwre": (
        lambda cond: lambda then_val: lambda else_val: (
            then_val if cond else else_val
        )
    ),
}


def _raise_type_err(prim_name, val):
  raise TypeError(
      f"Primitive '{prim_name}' expected a list, but got {type(val).__name__}:"
      f" {val}"
  )

# ---------------------------------------------------------------------------
# 2. S-Expression Parser & Short-Circuit Evaluator
# ---------------------------------------------------------------------------
def tokenize(s):
    return s.replace("(", " ( ").replace(")", " ) ").split()

def parse_tokens(tokens):
    if not tokens:
        raise SyntaxError("Unexpected EOF while parsing")
    token = tokens.pop(0)
    if token == "(":
        tree = []
        while tokens and tokens[0] != ")":
            tree.append(parse_tokens(tokens))
        if not tokens:
            raise SyntaxError("Unmatched '(' in expression")
        tokens.pop(0)
        return tree
    elif token == ")":
        raise SyntaxError("Unexpected ')'")
    return token

def eval_ast(ast, env):
    """
    env is a list where env[i] corresponds to de Bruijn index $i.
    """
    if isinstance(ast, str):
        if ast.startswith("$"):
            idx = int(ast[1:])
            if idx >= len(env):
                raise IndexError(f"Unbound de Bruijn index: ${idx} (env depth: {len(env)})")
            return env[idx]
        elif ast in ENV_PRIMITIVES:
            return ENV_PRIMITIVES[ast]
        else:
            raise ValueError(f"Unknown primitive or symbol: {ast}")

    if isinstance(ast, list):
        if not ast:
            raise ValueError("Empty list in AST evaluation")

        # Lambda abstraction: (lambda body)
        if ast[0] == "lambda":
            if len(ast) != 2:
                raise SyntaxError(f"Malformed lambda: {ast}")
            body = ast[1]
            return lambda arg: eval_ast(body, [arg] + env)

        # Short-circuiting if-then-else: (ewwre cond yes no)
        if ast[0] == "ewwre" and len(ast) == 4:
            cond_val = eval_ast(ast[1], env)
            return eval_ast(ast[2], env) if cond_val else eval_ast(ast[3], env)

        # Function application: (f arg1 arg2 ... argN)
        fn = eval_ast(ast[0], env)
        for arg_ast in ast[1:]:
            arg_val = eval_ast(arg_ast, env)
            fn = fn(arg_val)
        return fn

    return ast

def run_program(program_str, input_val):
    tokens = tokenize(program_str)
    ast = parse_tokens(tokens)
    fn = eval_ast(ast, env=[])
    return fn(input_val)

# ---------------------------------------------------------------------------
# 3. Dedup Test Cases
# ---------------------------------------------------------------------------
dedup_test_cases = [
    ([1, 2, 2, 3, 1], [1, 2, 3]),
    ([4, 4, 4, 4], [4]),
    ([5, 1, 2, 1, 5], [5, 1, 2]),
    ([2, 1, 1], [2, 1]),
    ([2, 1, 2], [2, 1]),
    ([13, 2, 5, 5], [13, 2, 5]),
]

def test_dedup_expression(expr):
    print(f"Testing expression:\n{expr}\n" + "-" * 60)
    all_passed = True
    for inp, expected in dedup_test_cases:
        try:
            actual = run_program(expr, inp)
            status = "PASS" if actual == expected else "FAIL"
            if status == "FAIL":
                all_passed = False
            print(f"[{status}] input: {inp} | expected: {expected} | got: {actual}")
        except Exception as e:
            all_passed = False
            print(f"[ERROR] input: {inp} | error: {e}")
    print("-" * 60)
    print("Result:", "ALL PASSED" if all_passed else "FAILED")

# ---------------------------------------------------------------------------
# 4. Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Test passed argument or fallback
    if len(sys.argv) > 1:
        test_dedup_expression(sys.argv[1])
    else:
        # Sum verification check
        sum_prog = "(lambda (abc1 $0 (lambda (lambda (ewwre (ajdfh? $0) 0 (+ (2aaaa $0) ($1 (ddj3 $0))))))))"
        print("Verification on sum_prog([1, 2, 3, 4]):", run_program(sum_prog, [1, 2, 3, 4]))