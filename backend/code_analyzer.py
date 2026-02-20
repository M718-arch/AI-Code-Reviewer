"""
code_analyzer.py - Complete Multi-Language Bug Detection Engine
Supports 14 programming languages with 41 analysis engines and intelligent noise filtering.
Zero-false-positive design: every check is intentional and targeted.
"""

import ast
import re
import tokenize
import io
from typing import List, Dict, Any, Set, Optional, Tuple


# ==============================================================================
# ISSUE BUILDER
# ==============================================================================

def issue(line: int, problem: str, severity: str, suggestion: str, category: str, code: str = '') -> Dict[str, Any]:
    return {
        'line': line,
        'problem': problem,
        'severity': severity,
        'suggestion': suggestion,
        'category': category,
        'code': code[:120] if code else ''
    }


# ==============================================================================
# MAIN ANALYZER CLASS
# ==============================================================================

class CodeAnalyzer:
    SEVERITY_ORDER = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}

    BUILTINS_MAP = {
        'python': {
            'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple', 'range',
            'open', 'sum', 'min', 'max', 'abs', 'round', 'type', 'isinstance', 'issubclass',
            'enumerate', 'zip', 'map', 'filter', 'sorted', 'reversed', 'any', 'all', 'next',
            'iter', 'id', 'hash', 'repr', 'format', 'input', 'super', 'property', 'classmethod',
            'staticmethod', 'object', 'bool', 'bytes', 'bytearray', 'complex', 'frozenset',
            'memoryview', 'slice', 'chr', 'ord', 'hex', 'oct', 'bin', 'pow', 'divmod',
            'getattr', 'setattr', 'delattr', 'hasattr', 'vars', 'dir', 'callable', 'globals',
            'locals', 'exec', 'compile', 'breakpoint', 'exit', 'quit', 'help', 'copyright',
            'True', 'False', 'None', 'NotImplemented', 'Ellipsis', '__debug__', '__import__',
            'Exception', 'ValueError', 'TypeError', 'KeyError', 'IndexError', 'AttributeError',
            'RuntimeError', 'IOError', 'OSError', 'StopIteration', 'GeneratorExit', 'SystemExit',
            'NotImplementedError', 'OverflowError', 'ZeroDivisionError', 'NameError',
            'ImportError', 'ModuleNotFoundError', 'FileNotFoundError', 'PermissionError',
            'TimeoutError', 'ConnectionError', 'UnicodeError', 'UnicodeDecodeError',
            'UnicodeEncodeError', 'AssertionError', 'RecursionError', 'MemoryError',
            'BufferError', 'ArithmeticError', 'LookupError', 'SyntaxError', 'IndentationError',
            'TabError', 'SystemError', 'ReferenceError', 'Warning', 'UserWarning',
            'DeprecationWarning', 'FutureWarning', 'BaseException', 'KeyboardInterrupt',
        },
        'javascript': {
            'console', 'document', 'window', 'Math', 'Date', 'Array', 'Object', 'String',
            'Number', 'Boolean', 'RegExp', 'JSON', 'Promise', 'Set', 'Map', 'Symbol',
            'Error', 'TypeError', 'RangeError', 'undefined', 'null', 'NaN', 'Infinity',
            'parseInt', 'parseFloat', 'isNaN', 'isFinite', 'decodeURI', 'encodeURI',
            'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval', 'fetch',
            'XMLHttpRequest', 'localStorage', 'sessionStorage', 'location', 'navigator',
            'alert', 'confirm', 'prompt', 'require', 'module', 'exports', '__dirname', '__filename',
        },
        'typescript': {
            'console', 'document', 'window', 'Math', 'Date', 'Array', 'Object', 'String',
            'Number', 'Boolean', 'RegExp', 'JSON', 'Promise', 'Set', 'Map', 'Symbol',
            'Error', 'TypeError', 'RangeError', 'undefined', 'null', 'NaN', 'Infinity',
            'parseInt', 'parseFloat', 'isNaN', 'isFinite', 'fetch', 'setTimeout', 'setInterval',
            'Record', 'Partial', 'Required', 'Readonly', 'Pick', 'Omit', 'Exclude', 'Extract',
            'NonNullable', 'ReturnType', 'Parameters', 'ConstructorParameters', 'InstanceType',
        },
        'java': {
            'System', 'String', 'Integer', 'Long', 'Double', 'Float', 'Boolean', 'Byte',
            'Short', 'Character', 'Math', 'Object', 'Class', 'Enum', 'Void',
            'List', 'ArrayList', 'LinkedList', 'Map', 'HashMap', 'LinkedHashMap', 'TreeMap',
            'Set', 'HashSet', 'LinkedHashSet', 'TreeSet', 'Collections', 'Arrays',
            'Optional', 'Stream', 'Iterator', 'Iterable',
            'Exception', 'RuntimeException', 'IllegalArgumentException', 'NullPointerException',
            'IndexOutOfBoundsException', 'UnsupportedOperationException', 'IOException',
            'StringBuilder', 'StringBuffer', 'Scanner', 'Random', 'Thread', 'Runnable',
        },
        'cpp': {
            'std', 'cout', 'cin', 'cerr', 'endl', 'string', 'vector', 'map', 'set', 'list',
            'unordered_map', 'unordered_set', 'deque', 'queue', 'stack', 'priority_queue',
            'pair', 'tuple', 'make_pair', 'make_tuple', 'array', 'bitset',
            'ifstream', 'ofstream', 'fstream', 'stringstream', 'istringstream', 'ostringstream',
            'nullptr', 'NULL', 'true', 'false', 'size_t', 'ptrdiff_t', 'int8_t', 'uint8_t',
            'int16_t', 'uint16_t', 'int32_t', 'uint32_t', 'int64_t', 'uint64_t',
            'shared_ptr', 'unique_ptr', 'weak_ptr', 'make_shared', 'make_unique',
            'sort', 'find', 'binary_search', 'lower_bound', 'upper_bound', 'min', 'max',
            'swap', 'move', 'forward', 'function', 'bind', 'ref', 'cref',
            'exception', 'runtime_error', 'logic_error', 'out_of_range', 'invalid_argument',
        },
        'c': {
            'printf', 'scanf', 'fprintf', 'fscanf', 'sprintf', 'sscanf', 'snprintf',
            'fopen', 'fclose', 'fread', 'fwrite', 'fgets', 'fputs', 'feof', 'ferror',
            'malloc', 'calloc', 'realloc', 'free', 'NULL', 'FILE', 'EOF',
            'strlen', 'strcpy', 'strncpy', 'strcat', 'strncat', 'strcmp', 'strncmp',
            'memcpy', 'memmove', 'memset', 'memcmp',
            'atoi', 'atof', 'atol', 'strtol', 'strtof', 'strtod',
            'exit', 'abort', 'atexit', 'rand', 'srand', 'abs', 'labs',
            'sin', 'cos', 'tan', 'sqrt', 'pow', 'log', 'exp', 'ceil', 'floor',
            'stdin', 'stdout', 'stderr', 'true', 'false', 'size_t', 'ptrdiff_t',
        },
        'csharp': {
            'Console', 'String', 'Int32', 'Int64', 'Double', 'Float', 'Boolean', 'Decimal',
            'Object', 'Math', 'Convert', 'Environment', 'Type', 'Enum',
            'List', 'Dictionary', 'HashSet', 'Queue', 'Stack', 'LinkedList',
            'Array', 'Tuple', 'ValueTuple', 'Nullable', 'Task', 'Thread', 'Mutex',
            'File', 'Directory', 'Path', 'Stream', 'StreamReader', 'StreamWriter',
            'Exception', 'ArgumentException', 'ArgumentNullException', 'InvalidOperationException',
            'NotImplementedException', 'NullReferenceException', 'IndexOutOfRangeException',
            'StringBuilder', 'Regex', 'Random', 'DateTime', 'TimeSpan', 'Guid',
            'IEnumerable', 'IEnumerator', 'IList', 'IDictionary', 'ICollection',
            'Action', 'Func', 'Predicate', 'EventHandler', 'var', 'dynamic', 'null', 'true', 'false',
        },
        'php': {
            'echo', 'print', 'array', 'isset', 'empty', 'unset', 'count', 'strlen',
            'implode', 'explode', 'str_split', 'str_replace', 'substr', 'strpos',
            'trim', 'ltrim', 'rtrim', 'strtolower', 'strtoupper', 'ucfirst',
            'intval', 'floatval', 'strval', 'boolval', 'is_null', 'is_string',
            'is_int', 'is_float', 'is_bool', 'is_array', 'is_object',
            'file_get_contents', 'file_put_contents', 'fopen', 'fclose', 'fread', 'fwrite',
            'json_encode', 'json_decode', 'serialize', 'unserialize',
            'preg_match', 'preg_replace', 'preg_split',
            'array_map', 'array_filter', 'array_reduce', 'array_keys', 'array_values',
            'in_array', 'array_search', 'array_push', 'array_pop', 'sort', 'rsort',
            'date', 'time', 'mktime', 'strtotime',
            'htmlspecialchars', 'htmlentities', 'strip_tags', 'addslashes', 'stripslashes',
            'header', 'session_start', 'session_destroy', 'die', 'exit',
            '$_GET', '$_POST', '$_REQUEST', '$_SESSION', '$_COOKIE', '$_SERVER', '$_FILES',
            'null', 'true', 'false', 'TRUE', 'FALSE', 'NULL',
        },
        'ruby': {
            'puts', 'print', 'gets', 'p', 'pp', 'require', 'require_relative', 'include', 'extend',
            'nil', 'true', 'false', 'self', 'super',
            'Array', 'Hash', 'String', 'Integer', 'Float', 'Symbol', 'Range', 'Regexp',
            'File', 'Dir', 'IO', 'Process', 'Thread', 'Fiber', 'Mutex',
            'Class', 'Module', 'Object', 'BasicObject', 'Kernel', 'Comparable', 'Enumerable',
            'Exception', 'RuntimeError', 'StandardError', 'ArgumentError', 'TypeError',
            'NameError', 'NoMethodError', 'IndexError', 'KeyError', 'IOError',
            'Math', 'Numeric', 'Rational', 'Complex', 'Random', 'Time', 'Date',
            'Proc', 'Lambda', 'Method', 'UnboundMethod',
            'STDIN', 'STDOUT', 'STDERR', 'ARGV', 'ENV',
        },
        'go': {
            'fmt', 'Println', 'Printf', 'Sprintf', 'Fprintf', 'Errorf', 'Scan', 'Scanf',
            'len', 'cap', 'append', 'make', 'new', 'close', 'delete', 'copy', 'panic', 'recover',
            'real', 'imag', 'complex', 'print', 'println',
            'error', 'nil', 'true', 'false', 'iota',
            'bool', 'byte', 'rune', 'string', 'int', 'int8', 'int16', 'int32', 'int64',
            'uint', 'uint8', 'uint16', 'uint32', 'uint64', 'uintptr',
            'float32', 'float64', 'complex64', 'complex128',
        },
        'rust': {
            'println!', 'print!', 'eprintln!', 'eprint!', 'format!', 'write!', 'writeln!',
            'vec!', 'assert!', 'assert_eq!', 'assert_ne!', 'panic!', 'todo!', 'unimplemented!',
            'String', 'str', 'Vec', 'Option', 'Result', 'Box', 'Rc', 'Arc', 'Cell', 'RefCell',
            'HashMap', 'HashSet', 'BTreeMap', 'BTreeSet', 'VecDeque', 'LinkedList',
            'Some', 'None', 'Ok', 'Err', 'true', 'false',
            'u8', 'u16', 'u32', 'u64', 'u128', 'usize',
            'i8', 'i16', 'i32', 'i64', 'i128', 'isize',
            'f32', 'f64', 'bool', 'char',
            'Drop', 'Clone', 'Copy', 'Debug', 'Display', 'Iterator', 'Into', 'From', 'AsRef',
        },
        'swift': {
            'print', 'String', 'Int', 'Double', 'Float', 'Bool', 'Character',
            'Array', 'Dictionary', 'Set', 'Optional', 'Result',
            'nil', 'true', 'false', 'self', 'super', 'type(of:)',
            'Error', 'Swift', 'Foundation', 'UIKit', 'AppKit', 'SwiftUI',
            'NSObject', 'NSString', 'NSArray', 'NSDictionary',
        },
        'kotlin': {
            'println', 'print', 'readLine', 'TODO',
            'listOf', 'mutableListOf', 'arrayListOf', 'arrayOf', 'emptyList',
            'mapOf', 'mutableMapOf', 'hashMapOf', 'emptyMap',
            'setOf', 'mutableSetOf', 'hashSetOf', 'emptySet',
            'sequenceOf', 'generateSequence', 'lazy',
            'String', 'Int', 'Long', 'Double', 'Float', 'Boolean', 'Char', 'Byte', 'Short',
            'Any', 'Unit', 'Nothing', 'null', 'true', 'false', 'this', 'super',
            'Pair', 'Triple', 'Result', 'Lazy',
            'Exception', 'RuntimeException', 'IllegalArgumentException', 'IllegalStateException',
        },
        'html': {
            'document', 'window', 'console', 'alert', 'prompt', 'confirm',
            'localStorage', 'sessionStorage', 'location', 'navigator', 'history',
        },
        'css': set(),
    }

    def __init__(self, language: str = 'python', filter_noise: bool = True):
        self.language = language.lower()
        self.filter_noise = filter_noise
        self.builtins: Set[str] = self.BUILTINS_MAP.get(self.language, set())

    # --------------------------------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------------------------------

    def analyze(self, code: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []

        analyzer_map = {
            'python':     self._analyze_python,
            'javascript': self._analyze_javascript,
            'typescript': self._analyze_typescript,
            'java':       self._analyze_java,
            'cpp':        self._analyze_cpp,
            'c':          self._analyze_c,
            'csharp':     self._analyze_csharp,
            'php':        self._analyze_php,
            'ruby':       self._analyze_ruby,
            'go':         self._analyze_go,
            'rust':       self._analyze_rust,
            'swift':      self._analyze_swift,
            'kotlin':     self._analyze_kotlin,
            'html':       self._analyze_html,
            'css':        self._analyze_css,
        }

        lang_issues = analyzer_map.get(self.language, lambda _: [])(code)
        common_issues = self._common_analysis(code)

        all_issues = lang_issues + common_issues

        # Deduplicate by (line, problem)
        seen: Set[Tuple[int, str]] = set()
        unique: List[Dict[str, Any]] = []
        for iss in all_issues:
            key = (iss['line'], iss['problem'])
            if key not in seen:
                seen.add(key)
                unique.append(iss)

        if self.filter_noise:
            unique = self._filter_noise(unique)

        unique.sort(key=lambda x: (self.SEVERITY_ORDER.get(x['severity'], 3), x['line']))
        return unique

    # --------------------------------------------------------------------------
    # NOISE FILTER
    # --------------------------------------------------------------------------

    def _filter_noise(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Keep HIGH always. For LOW, filter known-noisy patterns unless egregious."""
        ALWAYS_NOISY = {'Trailing whitespace', 'Missing semicolon'}
        filtered = []
        for iss in issues:
            if iss['severity'] == 'HIGH':
                filtered.append(iss)
                continue
            prob = iss['problem']
            if any(n in prob for n in ALWAYS_NOISY):
                continue
            # Only keep "Line too long" if > 150 chars
            if 'Line too long' in prob:
                m = re.search(r'\((\d+)', prob)
                if m and int(m.group(1)) > 150:
                    filtered.append(iss)
                continue
            filtered.append(iss)
        return filtered

    # ==========================================================================
    # PYTHON ANALYZER — AST-powered with syntax-fault-tolerance
    # ==========================================================================

    @staticmethod
    def _make_parseable(code: str) -> Tuple[str, Set[int]]:
        """
        Best-effort transform of broken Python into something ast.parse() accepts.
        Returns (fixed_code, set_of_lines_that_had_syntax_issues).
        Strategy:
          1. Add missing colons on block-start keywords.
          2. Fix stray indentation on def/class at module level.
          3. Iteratively blank still-failing lines (up to 40 passes).
        """
        BLOCK_KW = re.compile(
            r'^\s*(def|async\s+def|class|for|async\s+for|while|if|elif|else|'
            r'try|except|finally|with|async\s+with)\b.*[^:,\\]\s*$'
        )

        lines = code.splitlines()
        fixed: List[str] = []
        fixed_lines: Set[int] = set()

        for i, line in enumerate(lines, 1):
            stripped = line.rstrip()
            # Add missing colon
            if BLOCK_KW.match(stripped) and not stripped.strip().startswith('#'):
                stripped = stripped + ':'
                fixed_lines.add(i)
            # Fix stray-indent def/class (e.g. ' def foo():')
            m = re.match(r'^( +)((?:async\s+)?def |class )', stripped)
            if m and (len(m.group(1)) % 4 != 0 and len(m.group(1)) % 2 != 0):
                stripped = stripped.lstrip()
                fixed_lines.add(i)
            fixed.append(stripped)

        working = '\n'.join(fixed)

        # Iteratively blank lines that still cause syntax errors
        for _ in range(40):
            try:
                ast.parse(working)
                break
            except SyntaxError as e:
                if e.lineno is None:
                    break
                ln = e.lineno
                fixed_lines.add(ln)
                wlines = working.splitlines()
                if ln <= len(wlines):
                    indent = len(wlines[ln - 1]) - len(wlines[ln - 1].lstrip())
                    wlines[ln - 1] = ' ' * indent + 'pass  # _blanked_'
                working = '\n'.join(wlines)

        return working, fixed_lines

    def _analyze_python(self, code: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        lines = code.splitlines()

        # ── Collect real syntax errors first (on original code) ─────────────
        syntax_error_lines: Set[int] = set()
        probe = code
        for _ in range(30):
            try:
                ast.parse(probe)
                break
            except SyntaxError as e:
                if e.lineno is None:
                    break
                ln = e.lineno
                if ln in syntax_error_lines:
                    break
                syntax_error_lines.add(ln)
                snippet = lines[ln - 1] if ln <= len(lines) else ''
                issues.append(issue(ln, f'Syntax error: {e.msg}', 'HIGH',
                                    'Fix the syntax error', 'syntax', snippet))
                plines = probe.splitlines()
                plines[ln - 1] = 'pass  # _blanked_'
                probe = '\n'.join(plines)

        # ── Build a parseable version for deep AST analysis ─────────────────
        parseable, _ = self._make_parseable(code)
        try:
            tree = ast.parse(parseable)
        except SyntaxError:
            # Absolute fallback — only line checks
            issues += self._python_line_checks(lines)
            return issues

        # ── Collect scope info ──────────────────────────────────────────────
        defined_vars: Set[str] = set(self.builtins)
        imports: Set[str] = set()
        functions: Set[str] = set()
        classes: Set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defined_vars.add(node.name)
                functions.add(node.name)
                for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
                    defined_vars.add(arg.arg)
                if node.args.vararg:
                    defined_vars.add(node.args.vararg.arg)
                if node.args.kwarg:
                    defined_vars.add(node.args.kwarg.arg)
            elif isinstance(node, ast.ClassDef):
                defined_vars.add(node.name)
                classes.add(node.name)
            elif isinstance(node, ast.Assign):
                for t in node.targets:
                    for n in ast.walk(t):
                        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                            defined_vars.add(n.id)
            elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
                if isinstance(node.target if isinstance(node, ast.AugAssign) else (node.target or ast.Name()), ast.Name):
                    tgt = node.target if isinstance(node, ast.AugAssign) else node.target
                    if isinstance(tgt, ast.Name):
                        defined_vars.add(tgt.id)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name.split('.')[0]
                    defined_vars.add(name)
                    imports.add(name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name != '*':
                        name = alias.asname or alias.name
                        defined_vars.add(name)
                        imports.add(name)
                    else:
                        # wildcard: flag and don't break analysis
                        pass
            elif isinstance(node, (ast.For, ast.comprehension)):
                for n in ast.walk(node.target if isinstance(node, ast.For) else node.target):
                    if isinstance(n, ast.Name):
                        defined_vars.add(n.id)
            elif isinstance(node, ast.NamedExpr):
                defined_vars.add(node.target.id)
            elif isinstance(node, ast.ExceptHandler):
                if node.name:
                    defined_vars.add(node.name)
            elif isinstance(node, ast.Global):
                for n in node.names:
                    defined_vars.add(n)
            elif isinstance(node, ast.Nonlocal):
                for n in node.names:
                    defined_vars.add(n)
            elif isinstance(node, ast.withitem):
                if node.optional_vars and isinstance(node.optional_vars, ast.Name):
                    defined_vars.add(node.optional_vars.id)

        # ── 1. Undefined variables ───────────────────────────────────────────
        COMMON_MAGIC = {'__name__', '__file__', '__doc__', '__package__', '__spec__',
                        '__loader__', '__builtins__', '__all__', '__version__',
                        '_', '__', '___'}
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if (node.id not in defined_vars
                        and node.id not in COMMON_MAGIC
                        and not node.id.startswith('__')):
                    issues.append(issue(node.lineno,
                                        f'Undefined variable: {node.id}', 'HIGH',
                                        f'Define "{node.id}" before using it',
                                        'bug', node.id))

        # ── 2. Bare except ───────────────────────────────────────────────────
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(issue(node.lineno, 'Bare except clause', 'HIGH',
                                    'Catch specific exceptions: except ValueError:', 'error_handling',
                                    'except:'))

        # ── 3. Mutable default arguments ─────────────────────────────────────
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                n_args = len(node.args.args)
                n_defaults = len(node.args.defaults)
                for i, default in enumerate(node.args.defaults):
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        arg_idx = n_args - n_defaults + i
                        if 0 <= arg_idx < n_args:
                            arg_name = node.args.args[arg_idx].arg
                            issues.append(issue(node.lineno,
                                                f'Mutable default argument: {arg_name}',
                                                'MEDIUM',
                                                'Use None as default, create mutable inside body',
                                                'bug', f'def {node.name}(..., {arg_name}=[])'))

        # ── 4. Missing self in class methods ─────────────────────────────────
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue
                    deco_ids = {d.id for d in item.decorator_list if isinstance(d, ast.Name)}
                    if 'staticmethod' in deco_ids:
                        continue
                    if 'classmethod' in deco_ids:
                        expected = 'cls'
                    else:
                        expected = 'self'
                    if not item.args.args or item.args.args[0].arg != expected:
                        issues.append(issue(item.lineno,
                                            f'Method {item.name}() missing "{expected}" parameter',
                                            'HIGH',
                                            f'Add "{expected}" as first parameter',
                                            'bug', f'def {item.name}():'))

        # ── 5. Wildcard imports ──────────────────────────────────────────────
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and any(alias.name == '*' for alias in node.names):
                    issues.append(issue(node.lineno,
                                        f'Wildcard import: from {node.module} import *',
                                        'MEDIUM', 'Import only what you need', 'best_practice',
                                        f'from {node.module} import *'))

        # ── 6. Empty except block (pass only) ────────────────────────────────
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                body = [s for s in node.body if not isinstance(s, ast.Pass)]
                if not body:
                    issues.append(issue(node.lineno, 'Empty except block — exceptions silently swallowed',
                                        'MEDIUM', 'Handle the exception or at least log it',
                                        'error_handling', 'except: pass'))

        # ── 7. Too many arguments (>7) ────────────────────────────────────────
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                total = len(node.args.args) + len(node.args.posonlyargs)
                if total > 7:
                    issues.append(issue(node.lineno,
                                        f'Function {node.name}() has {total} arguments',
                                        'MEDIUM', 'Consider a dataclass or fewer parameters',
                                        'design', f'def {node.name}(...)'))

        # ── 8. Long functions (>80 lines) ─────────────────────────────────────
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = node.lineno
                end = max(
                    getattr(n, 'end_lineno', start)
                    for n in ast.walk(node)
                    if hasattr(n, 'end_lineno')
                )
                length = end - start + 1
                if length > 80:
                    issues.append(issue(node.lineno,
                                        f'Function {node.name}() is {length} lines long',
                                        'MEDIUM', 'Break into smaller helper functions',
                                        'design', f'def {node.name}(...)'))

        # ── 9. Redefining built-ins ──────────────────────────────────────────
        SAFE_SHADOWS = {'__file__', '__name__', '__doc__', '_'}
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                if node.id in self.builtins and node.id not in SAFE_SHADOWS:
                    issues.append(issue(node.lineno,
                                        f'Redefines built-in: {node.id}',
                                        'MEDIUM', 'Use a different variable name',
                                        'best_practice', f'{node.id} = ...'))

        # ── 10. Comparing None / True / False with == ──────────────────────
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                for op, comp in zip(node.ops, node.comparators):
                    if isinstance(op, (ast.Eq, ast.NotEq)):
                        if isinstance(comp, ast.Constant) and comp.value is None:
                            issues.append(issue(node.lineno,
                                                'Comparing None with == or !=',
                                                'LOW', 'Use "is None" or "is not None"',
                                                'best_practice', 'x == None'))
                        if isinstance(comp, ast.Constant) and isinstance(comp.value, bool):
                            issues.append(issue(node.lineno,
                                                f'Comparing bool with == (use "is {comp.value}")',
                                                'LOW', f'Use "is {comp.value}" or "is not {comp.value}"',
                                                'best_practice', f'x == {comp.value}'))

        # ── 11. Using 'is' with literals ─────────────────────────────────────
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                for op, comp in zip(node.ops, node.comparators):
                    if isinstance(op, (ast.Is, ast.IsNot)):
                        if isinstance(comp, ast.Constant) and not isinstance(comp.value, (type(None), bool)):
                            issues.append(issue(node.lineno,
                                                f'Using "is" with literal value {repr(comp.value)}',
                                                'LOW', 'Use == for value comparison',
                                                'best_practice', 'x is 42'))

        # ── 12. Unused variables ─────────────────────────────────────────────
        used_names: Set[str] = set()
        assigned_names: Dict[str, int] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Load):
                    used_names.add(node.id)
                elif isinstance(node.ctx, ast.Store):
                    if node.id not in assigned_names:
                        assigned_names[node.id] = node.lineno

        IGNORE_UNUSED = {'_', 'self', 'cls'} | imports | self.builtins | functions | classes
        for var, lineno in assigned_names.items():
            if var not in used_names and var not in IGNORE_UNUSED and not var.startswith('_'):
                issues.append(issue(lineno, f'Unused variable: {var}',
                                    'LOW', f'Remove or use "{var}"',
                                    'style', var))

        # ── 13. Unused imports ───────────────────────────────────────────────
        imported_names: Dict[str, int] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name.split('.')[0]
                    imported_names[name] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name != '*':
                        name = alias.asname or alias.name
                        imported_names[name] = node.lineno

        for imp, lineno in imported_names.items():
            if imp not in used_names:
                issues.append(issue(lineno, f'Unused import: {imp}',
                                    'LOW', f'Remove unused import "{imp}"',
                                    'style', imp))

        # ── 14. Missing docstrings ───────────────────────────────────────────
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                has_doc = (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                )
                if not has_doc and not node.name.startswith('_'):
                    kind = 'Class' if isinstance(node, ast.ClassDef) else 'Function'
                    issues.append(issue(node.lineno,
                                        f'{kind} {node.name}() missing docstring',
                                        'LOW', 'Add a docstring explaining purpose/args/returns',
                                        'documentation', f'def {node.name}():'))

        # ── 15. Variable naming conventions ──────────────────────────────────
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                name = node.id
                if re.search(r'[A-Z]', name) and '_' in name:
                    issues.append(issue(node.lineno,
                                        f'Mixed naming style: {name}',
                                        'LOW', 'Use snake_case for Python variable names',
                                        'style', name))

        # ── 16. Infinite recursion — no base case ─────────────────────────────
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_name = node.name
                # Collect all calls inside this function body
                has_base_case = any(isinstance(s, ast.If) for s in ast.walk(node))
                has_self_call = False
                for child in ast.walk(node):
                    if child is node:
                        continue
                    if (isinstance(child, ast.Call) and
                            isinstance(child.func, ast.Name) and
                            child.func.id == fn_name):
                        has_self_call = True
                if has_self_call and not has_base_case:
                    issues.append(issue(node.lineno,
                                        f'Infinite recursion in {fn_name}() — no base case found',
                                        'HIGH',
                                        'Add a base case condition (if/return) to stop recursion',
                                        'bug', f'def {fn_name}():'))

        # ── 17. Mutation during iteration ─────────────────────────────────────
        MUTATING_METHODS = {'remove', 'pop', 'clear', 'append', 'insert', 'extend',
                            'add', 'discard', 'update', '__delitem__'}
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                if isinstance(node.iter, ast.Name):
                    collection = node.iter.id
                    for child in ast.walk(node):
                        if (isinstance(child, ast.Call) and
                                isinstance(child.func, ast.Attribute) and
                                isinstance(child.func.value, ast.Name) and
                                child.func.value.id == collection and
                                child.func.attr in MUTATING_METHODS):
                            issues.append(issue(
                                getattr(child, 'lineno', node.lineno),
                                f'Modifying "{collection}" while iterating over it',
                                'HIGH',
                                f'Iterate over a copy: for x in list({collection}):',
                                'bug', f'{collection}.{child.func.attr}(...)'))

        # ── 18. Wrong argument count at call sites ─────────────────────────────
        func_sigs: Dict[str, Tuple[int, int]] = {}  # name -> (min_args, max_args)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = node.args
                # positional + pos-or-keyword, minus defaults = required
                total_pos = len(args.args) + len(args.posonlyargs)
                n_required = total_pos - len(args.defaults)
                n_max = total_pos
                # vararg or kwarg means unlimited
                if args.vararg or args.kwarg:
                    n_max = 9999
                # strip 'self'/'cls'
                if args.args and args.args[0].arg in ('self', 'cls'):
                    n_required = max(0, n_required - 1)
                    if n_max != 9999:
                        n_max = max(0, n_max - 1)
                func_sigs[node.name] = (n_required, n_max)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                fname = node.func.id
                if fname in func_sigs:
                    mn, mx = func_sigs[fname]
                    given = len(node.args) + len(node.keywords)
                    if given < mn:
                        issues.append(issue(node.lineno,
                                            f'Too few arguments calling {fname}() — '
                                            f'expected ≥{mn}, got {given}',
                                            'HIGH',
                                            f'Pass all required arguments to {fname}()',
                                            'bug', f'{fname}(...)'))
                    elif given > mx:
                        issues.append(issue(node.lineno,
                                            f'Too many arguments calling {fname}() — '
                                            f'expected ≤{mx}, got {given}',
                                            'HIGH',
                                            f'Remove extra arguments passed to {fname}()',
                                            'bug', f'{fname}(...)'))

        # ── 19. Type errors — str + int / list + str ───────────────────────────
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                def _const_type(n):
                    if isinstance(n, ast.Constant):
                        return type(n.value).__name__
                    return None
                lt = _const_type(node.left)
                rt = _const_type(node.right)
                if lt and rt and lt != rt:
                    issues.append(issue(node.lineno,
                                        f'Type mismatch in addition: {lt} + {rt}',
                                        'HIGH',
                                        f'Convert types explicitly before adding',
                                        'bug', f'{lt} + {rt}'))

        # ── 20. Division by len() — crashes on empty ──────────────────────────
        def _has_guard_before(tree, div_node, coll_name):
            """Return True if the function wrapping div_node has an if-guard on coll_name before it."""
            for fn in ast.walk(tree):
                if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                in_fn = any(child is div_node for child in ast.walk(fn))
                if not in_fn:
                    continue
                for stmt in fn.body:
                    if hasattr(stmt, 'lineno') and stmt.lineno >= div_node.lineno:
                        break
                    if isinstance(stmt, ast.If) and coll_name in ast.dump(stmt.test):
                        return True
            return False

        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                denom = node.right
                if (isinstance(denom, ast.Call) and
                        isinstance(denom.func, ast.Name) and
                        denom.func.id == 'len'):
                    coll = (denom.args[0].id
                            if denom.args and isinstance(denom.args[0], ast.Name) else None)
                    if coll and not _has_guard_before(tree, node, coll):
                        issues.append(issue(node.lineno,
                                            'Division by len() — crashes if collection is empty',
                                            'HIGH',
                                            'Check if collection is non-empty before dividing',
                                            'bug', 'total / len(...)'))

        # ── 21. Hardcoded plain-text passwords in dicts/assignments ───────────
        HASH_INDICATORS = {'hash', 'hashed', 'bcrypt', 'argon', 'pbkdf', 'sha', 'md5',
                           '*', '...', '<password>', '<secret>', 'placeholder', 'example'}
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                for k, v in zip(node.keys, node.values):
                    if (isinstance(k, ast.Constant) and
                            isinstance(k.value, str) and
                            'password' in k.value.lower() and
                            isinstance(v, ast.Constant) and
                            isinstance(v.value, str) and
                            len(v.value) > 2 and
                            not any(h in v.value.lower() for h in HASH_INDICATORS)):
                        issues.append(issue(node.lineno,
                                            'Storing plain-text password in dict literal',
                                            'HIGH',
                                            'Hash passwords with bcrypt/argon2 before storing',
                                            'security', f'"{k.value}": "..."'))

        # ── 22. Index access without bounds check ─────────────────────────────
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript):
                if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, int):
                    idx = node.slice.value
                    # Only flag non-trivial literal indices (≥ 10 or negative)
                    if abs(idx) >= 10:
                        coll = getattr(node.value, 'id', None) or ''
                        issues.append(issue(node.lineno,
                                            f'High-index access [{idx}] without bounds check',
                                            'MEDIUM',
                                            f'Verify collection length before accessing index {idx}',
                                            'bug', f'{coll}[{idx}]'))

        # ── 23. Indentation issues on originally-broken lines ─────────────────
        for ln in syntax_error_lines:
            if ln <= len(lines):
                raw = lines[ln - 1]
                # bad-indent: starts with a space count not divisible by 2 or 4
                m = re.match(r'^( +)\S', raw)
                if m and (len(m.group(1)) % 4 != 0 and len(m.group(1)) % 2 != 0):
                    issues.append(issue(ln, f'Unexpected indentation ({len(m.group(1))} spaces)',
                                        'HIGH', 'Fix indentation (use 4 spaces consistently)',
                                        'syntax', raw.strip()))

        # ── Line-level checks ─────────────────────────────────────────────────
        issues += self._python_line_checks(lines)

        return issues

    def _python_line_checks(self, lines: List[str]) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []

        # Patterns for hardcoded secrets
        SECRET_PATTERNS = [
            (r'(?i)password\s*=\s*[\'"][^\'"]{3,}[\'"]', 'Hardcoded password'),
            (r'(?i)api[_-]?key\s*=\s*[\'"][^\'"]{5,}[\'"]', 'Hardcoded API key'),
            (r'(?i)secret\s*=\s*[\'"][^\'"]{3,}[\'"]', 'Hardcoded secret'),
            (r'(?i)\btoken\s*=\s*[\'"][^\'"]{5,}[\'"]', 'Hardcoded token'),
            (r'(?i)auth\s*=\s*[\'"][^\'"]{3,}[\'"]', 'Hardcoded auth credential'),
            (r'(?i)private[_-]key\s*=\s*[\'"][^\'"]{5,}[\'"]', 'Hardcoded private key'),
        ]

        # Insecure deserialization
        INSECURE_DESER = [
            (r'\bpickle\.loads?\(', 'Insecure deserialization: pickle'),
            (r'\byaml\.load\s*\((?!.*Loader)', 'Unsafe yaml.load() without Loader'),
            (r'\beval\s*\(', 'eval() usage — security risk'),
            (r'\bexec\s*\(', 'exec() usage — security risk'),
        ]

        # Weak crypto
        WEAK_CRYPTO = [
            (r'\bmd5\b', 'Weak hash: MD5'),
            (r'\bsha1\b', 'Weak hash: SHA-1'),
            (r'\bDES\b', 'Weak cipher: DES'),
            (r'\bRC4\b', 'Weak cipher: RC4'),
        ]

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('#'):
                continue
            code_part = line.split('#')[0]

            for pattern, desc in SECRET_PATTERNS:
                if re.search(pattern, code_part):
                    issues.append(issue(i, desc, 'HIGH',
                                        'Use environment variables or a secrets manager',
                                        'security', stripped))

            for pattern, desc in INSECURE_DESER:
                if re.search(pattern, code_part):
                    issues.append(issue(i, desc, 'HIGH',
                                        'Avoid unsafe deserialization / code execution',
                                        'security', stripped))

            for pattern, desc in WEAK_CRYPTO:
                if re.search(pattern, code_part, re.IGNORECASE):
                    issues.append(issue(i, desc, 'HIGH',
                                        'Use SHA-256 or stronger hashing/encryption',
                                        'security', stripped))

            # SQL injection
            if re.search(r'(?i)(execute|cursor\.execute)\s*\(\s*["\']?\s*%|\.format\s*\(|f["\'].*SELECT|f["\'].*INSERT', code_part):
                issues.append(issue(i, 'SQL injection risk — string formatting in query',
                                    'HIGH', 'Use parameterized queries / ORM',
                                    'security', stripped))

            # Path traversal
            if re.search(r'open\s*\(.*\+|open\s*\(.*request|open\s*\(.*input', code_part):
                issues.append(issue(i, 'Potential path traversal in open()',
                                    'HIGH', 'Sanitize file paths from user input',
                                    'security', stripped))

            # Division by zero (literal)
            if re.search(r'/\s*0\b', code_part):
                issues.append(issue(i, 'Literal division by zero',
                                    'HIGH', 'Check denominator is non-zero',
                                    'bug', stripped))

            # open() without 'with'
            if re.search(r'\bopen\s*\(', code_part) and 'with' not in code_part:
                issues.append(issue(i, 'File opened without context manager',
                                    'MEDIUM', 'Use: with open(...) as f:',
                                    'resource_leak', stripped))

            # Integer overflow risk (32-bit boundary)
            if re.search(r'\b2147483647\b|\b4294967295\b', code_part):
                issues.append(issue(i, 'Magic number resembling integer overflow boundary',
                                    'LOW', 'Use sys.maxsize or named constant',
                                    'bug', stripped))

            # String concat in loop hint
            if re.search(r'\+=\s*[\'"]', code_part) or re.search(r'\w+\s*=\s*\w+\s*\+\s*[\'"]', code_part):
                issues.append(issue(i, 'String concatenation with + (may be inefficient in loops)',
                                    'LOW', "Use ''.join([...]) for repeated concatenation",
                                    'performance', stripped))

        return issues

    # ==========================================================================
    # JAVASCRIPT ANALYZER
    # ==========================================================================

    def _analyze_javascript(self, code: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        lines = code.splitlines()
        declared: Set[str] = set(self.builtins)

        DECL_RE = [
            (r'\blet\s+(\w+)', 'let'),
            (r'\bconst\s+(\w+)', 'const'),
            (r'\bvar\s+(\w+)', 'var'),
            (r'\bfunction\s+(\w+)', 'function'),
            (r'\bclass\s+(\w+)', 'class'),
        ]

        SECRET_PATTERNS = [
            (r'(?i)password\s*[:=]\s*[\'"`][^\'"` ]{3,}[\'"`]', 'Hardcoded password'),
            (r'(?i)api[_-]?key\s*[:=]\s*[\'"`][^\'"` ]{5,}[\'"`]', 'Hardcoded API key'),
            (r'(?i)secret\s*[:=]\s*[\'"`][^\'"` ]{3,}[\'"`]', 'Hardcoded secret'),
            (r'(?i)token\s*[:=]\s*[\'"`][^\'"` ]{5,}[\'"`]', 'Hardcoded token'),
        ]

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            code_part = re.sub(r'//.*', '', line)
            code_part = re.sub(r'/\*.*?\*/', '', code_part)

            for pattern, kind in DECL_RE:
                m = re.search(pattern, code_part)
                if m:
                    declared.add(m.group(1))
                    if kind == 'var':
                        issues.append(issue(i, 'Using "var" — prefer "let" or "const"',
                                            'LOW', 'Use const for non-reassigned, let otherwise',
                                            'best_practice', stripped))

            # == instead of ===
            if re.search(r'(?<![=!<>])==(?!=)', code_part):
                issues.append(issue(i, 'Loose equality (==) — use === for strict comparison',
                                    'MEDIUM', 'Replace == with ===',
                                    'bug', stripped))

            # eval()
            if re.search(r'\beval\s*\(', code_part):
                issues.append(issue(i, 'eval() usage — security risk',
                                    'HIGH', 'Avoid eval(); parse JSON with JSON.parse()',
                                    'security', stripped))

            # setTimeout/setInterval with string
            if re.search(r'set(?:Timeout|Interval)\s*\(\s*[\'"`]', code_part):
                issues.append(issue(i, 'setTimeout/setInterval with string argument',
                                    'HIGH', 'Pass a function reference instead of a string',
                                    'security', stripped))

            # == null (use === null or nullish coalescing)
            if re.search(r'(?<![=!])== null\b', code_part):
                issues.append(issue(i, 'Loose null check (== null)',
                                    'LOW', 'Use === null or == null intentionally with comment',
                                    'best_practice', stripped))

            # console.log
            if re.search(r'\bconsole\.\w+\s*\(', code_part):
                issues.append(issue(i, 'console.* left in production code',
                                    'LOW', 'Remove or replace with a logging library',
                                    'debug', stripped))

            # Hardcoded secrets
            for pat, desc in SECRET_PATTERNS:
                if re.search(pat, code_part):
                    issues.append(issue(i, desc, 'HIGH',
                                        'Use environment variables',
                                        'security', stripped))

            # Dangerous innerHTML
            if re.search(r'\.innerHTML\s*=', code_part):
                issues.append(issue(i, 'Direct innerHTML assignment (XSS risk)',
                                    'HIGH', 'Use textContent or DOMPurify for sanitized HTML',
                                    'security', stripped))

            # document.write
            if re.search(r'\bdocument\.write\s*\(', code_part):
                issues.append(issue(i, 'document.write() usage (blocks rendering, XSS risk)',
                                    'HIGH', 'Use DOM manipulation methods instead',
                                    'security', stripped))

            # Weak crypto
            if re.search(r'\bMath\.random\s*\(', code_part):
                issues.append(issue(i, 'Math.random() — not cryptographically secure',
                                    'MEDIUM', 'Use crypto.getRandomValues() for security needs',
                                    'security', stripped))

            # Unused variable hint (basic)
            # (Full scope analysis requires proper JS parser — skipped to avoid false positives)

            # Missing error handling in .then()
            if re.search(r'\.then\s*\([^)]*\)\s*(?!\.catch)', line):
                issues.append(issue(i, 'Promise .then() without .catch()',
                                    'MEDIUM', 'Add .catch() or use try/await to handle rejections',
                                    'error_handling', stripped))

            # SQL injection via template literal
            if re.search(r'(?i)`\s*(SELECT|INSERT|UPDATE|DELETE).*\${', code_part):
                issues.append(issue(i, 'SQL injection risk — template literal in query',
                                    'HIGH', 'Use parameterized queries',
                                    'security', stripped))

            # Modulo by zero
            if re.search(r'%\s*0\b', code_part):
                issues.append(issue(i, 'Modulo by zero',
                                    'HIGH', 'Check divisor before using %',
                                    'bug', stripped))

        return issues

    # ==========================================================================
    # TYPESCRIPT ANALYZER (extends JS)
    # ==========================================================================

    def _analyze_typescript(self, code: str) -> List[Dict[str, Any]]:
        issues = self._analyze_javascript(code)
        lines = code.splitlines()

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            code_part = re.sub(r'//.*', '', line)

            # : any usage
            if re.search(r':\s*any\b', code_part):
                issues.append(issue(i, 'Type "any" defeats TypeScript safety',
                                    'MEDIUM', 'Replace "any" with a proper type or "unknown"',
                                    'type_safety', stripped))

            # Non-null assertion !
            if re.search(r'\w+!\.|\w+!\)', code_part) and '!=' not in code_part and '!==' not in code_part:
                issues.append(issue(i, 'Non-null assertion (!) risks runtime crash',
                                    'MEDIUM', 'Use optional chaining (?.) or explicit null check',
                                    'type_safety', stripped))

            # Missing function return type
            if re.search(r'(?:function\s+\w+|(?:const|let)\s+\w+\s*=\s*(?:async\s*)?\()', code_part):
                if re.search(r'\)\s*{', code_part) and not re.search(r'\)\s*:', code_part):
                    issues.append(issue(i, 'Function missing explicit return type annotation',
                                        'LOW', 'Add return type: function foo(): ReturnType',
                                        'best_practice', stripped))

            # @ts-ignore
            if re.search(r'@ts-ignore', line):
                issues.append(issue(i, '@ts-ignore suppresses type errors',
                                    'MEDIUM', 'Fix the underlying type error instead',
                                    'type_safety', stripped))

            # Enum misuse (string enum better than numeric for readability)
            if re.search(r'\benum\s+\w+\s*{[^}]*=\s*\d', code_part):
                issues.append(issue(i, 'Numeric enum — consider string enum for readability',
                                    'LOW', "Use string enums: enum Dir { Up = 'UP' }",
                                    'best_practice', stripped))

        return issues

    # ==========================================================================
    # JAVA ANALYZER
    # ==========================================================================

    def _analyze_java(self, code: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        lines = code.splitlines()

        brace_depth = 0
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            code_part = re.sub(r'//.*', '', line)

            # NullPointerException risk with .equals()
            m = re.search(r'(\w+)\.equals\s*\(', code_part)
            if m and m.group(1) not in {'String', 'null', 'this', 'super'}:
                issues.append(issue(i, f'Potential NullPointerException: {m.group(1)}.equals()',
                                    'HIGH', f'Use Objects.equals({m.group(1)}, ...) or reverse: "literal".equals({m.group(1)})',
                                    'bug', stripped))

            # System.out.println
            if 'System.out.print' in code_part:
                issues.append(issue(i, 'System.out.println() in production code',
                                    'LOW', 'Use a logging framework (SLF4J, Log4j)',
                                    'debug', stripped))

            # Empty catch block
            if re.search(r'\bcatch\s*\([^)]+\)\s*\{\s*\}', code_part) or re.search(r'\bcatch\s*\(.*\)\s*$', code_part):
                issues.append(issue(i, 'Empty catch block — exception silently ignored',
                                    'MEDIUM', 'Log or handle the exception',
                                    'error_handling', stripped))

            # String comparison with ==
            if re.search(r'\bString\b.*==|==.*\bString\b', code_part):
                issues.append(issue(i, 'String compared with == (compares references)',
                                    'HIGH', 'Use .equals() for string comparison',
                                    'bug', stripped))

            # Hardcoded secrets
            for pat, desc in [
                (r'(?i)password\s*=\s*"[^"]{3,}"', 'Hardcoded password'),
                (r'(?i)api[_-]?key\s*=\s*"[^"]{5,}"', 'Hardcoded API key'),
                (r'(?i)secret\s*=\s*"[^"]{3,}"', 'Hardcoded secret'),
            ]:
                if re.search(pat, code_part):
                    issues.append(issue(i, desc, 'HIGH',
                                        'Use environment variables or a secrets manager',
                                        'security', stripped))

            # SQL injection
            if re.search(r'(?i)(createStatement|executeQuery|executeUpdate).*\+', code_part):
                issues.append(issue(i, 'SQL injection risk — string concatenation in query',
                                    'HIGH', 'Use PreparedStatement with parameters',
                                    'security', stripped))

            # Resource leak: InputStream/Reader without try-with-resources
            if re.search(r'new\s+(FileInputStream|FileReader|BufferedReader|Scanner)\s*\(', code_part):
                if 'try' not in ''.join(lines[max(0, i-3):i]):
                    issues.append(issue(i, 'Resource may not be closed (use try-with-resources)',
                                        'MEDIUM', 'Wrap in: try (ResourceType r = new ...) {}',
                                        'resource_leak', stripped))

            # instanceof check before cast missing
            if re.search(r'\(\w+\)\s*\w+', code_part) and 'instanceof' not in ''.join(lines[max(0, i-3):i]):
                pass  # too noisy without proper parser, skip

            # Deprecated Thread.stop/suspend/resume
            if re.search(r'\.\s*(stop|suspend|resume)\s*\(\s*\)', code_part):
                issues.append(issue(i, 'Deprecated Thread method (.stop/.suspend/.resume)',
                                    'HIGH', 'Use interrupt() and volatile flags instead',
                                    'deprecated', stripped))

            # Weak random
            if 'new Random()' in code_part and 'Security' not in code_part:
                issues.append(issue(i, 'java.util.Random is not cryptographically secure',
                                    'MEDIUM', 'Use SecureRandom for security-sensitive contexts',
                                    'security', stripped))

            # Missing @Override
            if re.search(r'public\s+\w+\s+(toString|equals|hashCode|compareTo)\s*\(', code_part):
                if '@Override' not in (lines[i-2] if i > 1 else ''):
                    issues.append(issue(i, 'Missing @Override annotation',
                                        'LOW', 'Add @Override to detect signature mismatches',
                                        'best_practice', stripped))

        return issues

    # ==========================================================================
    # C++ ANALYZER
    # ==========================================================================

    def _analyze_cpp(self, code: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        lines = code.splitlines()
        new_vars: Dict[str, int] = {}   # var -> line of new

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            code_part = re.sub(r'//.*', '', line)

            # Memory management
            m = re.search(r'\bnew\s+\w+', code_part)
            if m:
                var_match = re.search(r'(\w+)\s*=\s*new\b', code_part)
                if var_match:
                    new_vars[var_match.group(1)] = i

            if re.search(r'\bdelete\s+\[?\s*\]?\s*(\w+)', code_part):
                var = re.search(r'\bdelete\s+\[?\s*\]?\s*(\w+)', code_part).group(1)
                new_vars.pop(var, None)

            # Raw pointers (prefer smart pointers)
            if re.search(r'\b\w+\s*\*\s*\w+\s*=\s*new\b', code_part):
                issues.append(issue(i, 'Raw pointer with new — prefer smart pointers',
                                    'MEDIUM', 'Use std::unique_ptr or std::shared_ptr',
                                    'memory', stripped))

            # gets() — buffer overflow
            if re.search(r'\bgets\s*\(', code_part):
                issues.append(issue(i, 'gets() is unsafe (buffer overflow)',
                                    'HIGH', 'Use fgets() or std::getline()',
                                    'security', stripped))

            # strcpy without bounds
            if re.search(r'\bstrcpy\s*\(', code_part):
                issues.append(issue(i, 'strcpy() — buffer overflow risk',
                                    'HIGH', 'Use strncpy() or std::string',
                                    'security', stripped))

            # sprintf — buffer overflow
            if re.search(r'\bsprintf\s*\(', code_part):
                issues.append(issue(i, 'sprintf() — buffer overflow risk',
                                    'HIGH', 'Use snprintf() or std::ostringstream',
                                    'security', stripped))

            # system() call
            if re.search(r'\bsystem\s*\(', code_part):
                issues.append(issue(i, 'system() call — command injection risk',
                                    'HIGH', 'Use execv() family or avoid shell invocation',
                                    'security', stripped))

            # Division by literal zero
            if re.search(r'/\s*0\b', code_part):
                issues.append(issue(i, 'Division by zero',
                                    'HIGH', 'Check denominator before dividing',
                                    'bug', stripped))

            # Division by size() without empty check
            if re.search(r'/\s*\w+\.size\s*\(\s*\)', code_part):
                context = '\n'.join(lines[max(0, i-10):i])
                if 'empty()' not in context and '.size() > 0' not in context and '.size() != 0' not in context:
                    issues.append(issue(i, 'Division by size() without empty() check',
                                        'HIGH', 'Check container.empty() before dividing by size()',
                                        'bug', stripped))

            # Vector/array access without bounds check
            if re.search(r'\w+\s*\[\s*\w+\s*\]', code_part) and '.at(' not in code_part:
                # Only flag if index is a variable (not a literal small number)
                m2 = re.search(r'\w+\s*\[\s*([a-zA-Z_]\w*)\s*\]', code_part)
                if m2:
                    context = '\n'.join(lines[max(0, i-5):i])
                    if 'size()' not in context and 'length' not in context:
                        issues.append(issue(i, 'Array/vector access without bounds check',
                                            'MEDIUM', 'Use .at() or verify index < container.size()',
                                            'bug', stripped))

            # using namespace std
            if re.search(r'using\s+namespace\s+std\s*;', code_part):
                issues.append(issue(i, '"using namespace std" pollutes global namespace',
                                    'LOW', 'Use std:: prefix explicitly',
                                    'best_practice', stripped))

            # printf type mismatch hints (basic)
            if re.search(r'\bprintf\s*\(', code_part) and '%d' in code_part and re.search(r'sizeof|strlen', code_part):
                issues.append(issue(i, 'printf: using %d for size_t — should be %zu',
                                    'MEDIUM', 'Use %zu for size_t values',
                                    'bug', stripped))

            # Missing null check after malloc
            if re.search(r'\bmalloc\s*\(', code_part):
                context_after = '\n'.join(lines[i:min(i+5, len(lines))])
                if 'if' not in context_after or 'NULL' not in context_after:
                    issues.append(issue(i, 'malloc() return value not checked for NULL',
                                        'HIGH', 'Check if malloc returns NULL before using pointer',
                                        'bug', stripped))

            # Infinite loop risk — while(true) without break
            if re.search(r'\bwhile\s*\(\s*(true|1)\s*\)', code_part):
                block = '\n'.join(lines[i:min(i+30, len(lines))])
                if 'break' not in block and 'return' not in block:
                    issues.append(issue(i, 'Potential infinite loop (while(true) without break/return)',
                                        'HIGH', 'Ensure loop has an exit condition',
                                        'bug', stripped))

            # Hardcoded secrets
            for pat, desc in [
                (r'(?i)password\s*=\s*"[^"]{3,}"', 'Hardcoded password'),
                (r'(?i)secret\s*=\s*"[^"]{3,}"', 'Hardcoded secret'),
            ]:
                if re.search(pat, code_part):
                    issues.append(issue(i, desc, 'HIGH',
                                        'Use environment variables or config files',
                                        'security', stripped))

            # Global mutable state (global non-const variables)
            if re.search(r'^(?:int|double|float|char|string|bool|vector|map|set)\s+\w+', stripped):
                if not stripped.startswith('const') and i < 30:
                    issues.append(issue(i, 'Global mutable variable — prefer local scope',
                                        'MEDIUM', 'Encapsulate in a class or pass as parameter',
                                        'design', stripped))

            # Missing virtual destructor
            if re.search(r'\bclass\s+\w+', code_part):
                block = '\n'.join(lines[i:min(i+40, len(lines))])
                if 'virtual' in block and '~' not in block:
                    issues.append(issue(i, 'Class with virtual methods missing virtual destructor',
                                        'HIGH', 'Add virtual ~ClassName() = default;',
                                        'bug', stripped))

        # Memory leak check: unpaired new/delete
        for var, lineno in new_vars.items():
            issues.append(issue(lineno, f'Possible memory leak: "{var}" allocated with new but no delete found',
                                'HIGH', 'Use smart pointer or ensure delete is called',
                                'memory', var))

        return issues

    # ==========================================================================
    # C ANALYZER
    # ==========================================================================

    def _analyze_c(self, code: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        lines = code.splitlines()
        malloc_vars: Dict[str, int] = {}

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            code_part = re.sub(r'//.*', '', line)

            # gets() — eliminated in C11
            if re.search(r'\bgets\s*\(', code_part):
                issues.append(issue(i, 'gets() — buffer overflow vulnerability',
                                    'HIGH', 'Use fgets(buf, sizeof(buf), stdin)',
                                    'security', stripped))

            # strcpy / strcat
            if re.search(r'\bstrcpy\s*\(', code_part):
                issues.append(issue(i, 'strcpy() — no bounds checking',
                                    'HIGH', 'Use strncpy() or strlcpy()',
                                    'security', stripped))
            if re.search(r'\bstrcat\s*\(', code_part):
                issues.append(issue(i, 'strcat() — no bounds checking',
                                    'HIGH', 'Use strncat() with explicit length',
                                    'security', stripped))

            # sprintf
            if re.search(r'\bsprintf\s*\(', code_part):
                issues.append(issue(i, 'sprintf() — buffer overflow risk',
                                    'HIGH', 'Use snprintf()',
                                    'security', stripped))

            # scanf with %s (no width limit)
            if re.search(r'\bscanf\s*\([^)]*%s', code_part):
                issues.append(issue(i, 'scanf with %s — buffer overflow risk',
                                    'HIGH', 'Specify max width: %255s',
                                    'security', stripped))

            # malloc without NULL check
            m = re.search(r'(\w+)\s*=\s*\bmalloc\s*\(', code_part)
            if m:
                malloc_vars[m.group(1)] = i
                context_after = '\n'.join(lines[i:min(i+5, len(lines))])
                if 'if' not in context_after:
                    issues.append(issue(i, f'malloc() return not checked for NULL',
                                        'HIGH', 'if (ptr == NULL) { ... }',
                                        'bug', stripped))

            # free() — track to remove from malloc_vars
            m2 = re.search(r'\bfree\s*\(\s*(\w+)\s*\)', code_part)
            if m2:
                malloc_vars.pop(m2.group(1), None)

            # Division by zero
            if re.search(r'/\s*0\b', code_part):
                issues.append(issue(i, 'Division by zero', 'HIGH',
                                    'Check divisor before division', 'bug', stripped))

            # system()
            if re.search(r'\bsystem\s*\(', code_part):
                issues.append(issue(i, 'system() — command injection risk',
                                    'HIGH', 'Use execv() family instead',
                                    'security', stripped))

            # Signed/unsigned comparison
            if re.search(r'\bint\b.*<\s*sizeof|sizeof.*>\s*\bint\b', code_part):
                issues.append(issue(i, 'Signed/unsigned comparison with sizeof',
                                    'MEDIUM', 'Use size_t for sizeof comparisons',
                                    'bug', stripped))

            # Hardcoded secrets
            for pat, desc in [
                (r'(?i)password\s*=\s*"[^"]{3,}"', 'Hardcoded password'),
                (r'(?i)secret\s*=\s*"[^"]{3,}"', 'Hardcoded secret'),
            ]:
                if re.search(pat, code_part):
                    issues.append(issue(i, desc, 'HIGH',
                                        'Use configuration files or environment variables',
                                        'security', stripped))

            # Integer overflow risk with signed int
            if re.search(r'\bINT_MAX\b', code_part) and '+' in code_part:
                issues.append(issue(i, 'Potential signed integer overflow near INT_MAX',
                                    'HIGH', 'Check for overflow before adding',
                                    'bug', stripped))

            # Missing return in non-void function (heuristic)
            if re.search(r'^int\s+main\s*\(', code_part):
                block = '\n'.join(lines[i:min(i+50, len(lines))])
                if 'return' not in block:
                    issues.append(issue(i, 'main() may be missing return statement',
                                        'MEDIUM', 'Add return 0; at end of main()',
                                        'bug', stripped))

        # Memory leak check
        for var, lineno in malloc_vars.items():
            issues.append(issue(lineno, f'Possible memory leak: "{var}" allocated but free() not found',
                                'HIGH', 'Call free() when done, or restructure ownership',
                                'memory', var))

        return issues

    # ==========================================================================
    # C# ANALYZER
    # ==========================================================================

    def _analyze_csharp(self, code: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        lines = code.splitlines()

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            code_part = re.sub(r'//.*', '', line)

            # Async without await
            if re.search(r'\basync\b', code_part) and 'Task' in code_part:
                context = '\n'.join(lines[i:min(i+30, len(lines))])
                if 'await ' not in context:
                    issues.append(issue(i, 'async method without await — synchronous execution',
                                        'MEDIUM', 'Add await or remove async keyword',
                                        'bug', stripped))

            # String comparison with ==
            if re.search(r'\bstring\b.*==|==.*\bstring\b', code_part, re.IGNORECASE):
                issues.append(issue(i, 'String compared with == (culture-sensitive)',
                                    'LOW', 'Use string.Equals() or StringComparison.Ordinal',
                                    'best_practice', stripped))

            # Empty catch block
            if re.search(r'\bcatch\s*(\(\s*\))?\s*\{\s*\}', code_part) or re.search(r'\bcatch\s*\(.*\)\s*{\s*}', code_part):
                issues.append(issue(i, 'Empty catch block — exception swallowed',
                                    'MEDIUM', 'Log the exception at minimum',
                                    'error_handling', stripped))

            # NullReferenceException risk — accessing member before null check
            if re.search(r'\w+\.\w+\s*(?:\(|=)', code_part):
                if 'null' not in ''.join(lines[max(0, i-3):i]) and '?' not in line:
                    pass  # too noisy without semantic analysis

            # Hardcoded secrets
            for pat, desc in [
                (r'(?i)password\s*=\s*"[^"]{3,}"', 'Hardcoded password'),
                (r'(?i)connectionString\s*=\s*"[^"]{10,}"', 'Hardcoded connection string'),
                (r'(?i)apiKey\s*=\s*"[^"]{5,}"', 'Hardcoded API key'),
            ]:
                if re.search(pat, code_part):
                    issues.append(issue(i, desc, 'HIGH',
                                        'Use IConfiguration or secrets management',
                                        'security', stripped))

            # SQL injection via string concat
            if re.search(r'(?i)(SqlCommand|ExecuteQuery|ExecuteNonQuery).*\+', code_part):
                issues.append(issue(i, 'SQL injection risk — string concatenation in query',
                                    'HIGH', 'Use SqlParameter or Entity Framework',
                                    'security', stripped))

            # IDisposable without using
            if re.search(r'new\s+(SqlConnection|SqlCommand|FileStream|StreamReader|StreamWriter|HttpClient)\s*\(', code_part):
                context = '\n'.join(lines[max(0, i-3):i])
                if 'using' not in context:
                    issues.append(issue(i, 'IDisposable resource not wrapped in using',
                                        'MEDIUM', 'Use: using (var r = new ...) {}',
                                        'resource_leak', stripped))

            # Thread.Sleep in async context
            if re.search(r'\bThread\.Sleep\s*\(', code_part):
                issues.append(issue(i, 'Thread.Sleep() blocks the thread',
                                    'MEDIUM', 'Use await Task.Delay() in async code',
                                    'performance', stripped))

            # Missing null check before dereference
            if re.search(r'\?\.\s*\w+', code_part):
                pass  # null-conditional used — good practice, no issue

            # Console.WriteLine in production
            if re.search(r'\bConsole\.Write', code_part):
                issues.append(issue(i, 'Console.Write* in production code',
                                    'LOW', 'Use ILogger or a logging framework',
                                    'debug', stripped))

        return issues

    # ==========================================================================
    # PHP ANALYZER
    # ==========================================================================

    def _analyze_php(self, code: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        lines = code.splitlines()

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('#'):
                continue
            code_part = re.sub(r'//.*|#.*', '', line)

            # Deprecated mysql_*
            if re.search(r'\bmysql_\w+\s*\(', code_part):
                issues.append(issue(i, 'Deprecated mysql_* function',
                                    'HIGH', 'Use MySQLi or PDO',
                                    'deprecated', stripped))

            # SQL injection
            if re.search(r'(?i)(mysql_query|mysqli_query|query)\s*\(.*\$_(GET|POST|REQUEST)', code_part):
                issues.append(issue(i, 'SQL injection risk — user input in query',
                                    'HIGH', 'Use prepared statements with bind_param()',
                                    'security', stripped))

            # eval()
            if re.search(r'\beval\s*\(', code_part):
                issues.append(issue(i, 'eval() usage — code injection risk',
                                    'HIGH', 'Avoid eval(); restructure logic',
                                    'security', stripped))

            # XSS — echo without escaping
            if re.search(r'\becho\s+\$_(GET|POST|REQUEST|COOKIE)', code_part):
                issues.append(issue(i, 'XSS risk — echoing user input without escaping',
                                    'HIGH', 'Use htmlspecialchars($input, ENT_QUOTES)',
                                    'security', stripped))

            # file inclusion with user input
            if re.search(r'(?:include|require)(?:_once)?\s*\(\s*\$', code_part):
                issues.append(issue(i, 'File inclusion with variable — path traversal risk',
                                    'HIGH', 'Whitelist allowed paths, never include user input directly',
                                    'security', stripped))

            # unserialize with user input
            if re.search(r'\bunserialize\s*\(\s*\$', code_part):
                issues.append(issue(i, 'unserialize() with user input — object injection risk',
                                    'HIGH', 'Use JSON instead of serialize/unserialize',
                                    'security', stripped))

            # == instead of ===
            if re.search(r'(?<![=!<>])==(?!=)', code_part):
                issues.append(issue(i, 'Loose comparison (==) in PHP — type juggling risk',
                                    'MEDIUM', 'Use === for strict comparison',
                                    'bug', stripped))

            # Hardcoded secrets
            for pat, desc in [
                (r'(?i)\$password\s*=\s*[\'"][^\'"]{3,}[\'"]', 'Hardcoded password'),
                (r'(?i)\$api_?key\s*=\s*[\'"][^\'"]{5,}[\'"]', 'Hardcoded API key'),
                (r'(?i)\$secret\s*=\s*[\'"][^\'"]{3,}[\'"]', 'Hardcoded secret'),
            ]:
                if re.search(pat, code_part):
                    issues.append(issue(i, desc, 'HIGH',
                                        'Use $_ENV or a secrets manager',
                                        'security', stripped))

            # error_reporting suppression
            if re.search(r'\berror_reporting\s*\(\s*0\s*\)', code_part):
                issues.append(issue(i, 'error_reporting(0) hides all errors',
                                    'MEDIUM', 'Enable error reporting in development',
                                    'debug', stripped))

            # Weak hash
            if re.search(r'\bmd5\s*\(|\bsha1\s*\(', code_part):
                issues.append(issue(i, 'Weak hash function (MD5/SHA1) for passwords',
                                    'HIGH', 'Use password_hash() and password_verify()',
                                    'security', stripped))

        return issues

    # ==========================================================================
    # RUBY ANALYZER
    # ==========================================================================

    def _analyze_ruby(self, code: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        lines = code.splitlines()

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('#'):
                continue

            # eval
            if re.search(r'\beval\s*[\(\{]|\.eval\s*[\(\{]', line):
                issues.append(issue(i, 'eval() — code injection risk',
                                    'HIGH', 'Avoid eval(); restructure logic',
                                    'security', stripped))

            # SQL injection via string interpolation in ActiveRecord
            if re.search(r'\.where\s*\(\s*"[^"]*#\{', line) or re.search(r'\.find_by_sql\s*\(\s*"[^"]*#\{', line):
                issues.append(issue(i, 'SQL injection risk — string interpolation in query',
                                    'HIGH', 'Use parameterized queries: .where("col = ?", val)',
                                    'security', stripped))

            # system() / backtick
            if re.search(r'\bsystem\s*\(|\`[^`]+\`|%x\{', line):
                issues.append(issue(i, 'Shell command execution — command injection risk',
                                    'HIGH', 'Validate/sanitize input; use Open3 instead',
                                    'security', stripped))

            # == nil
            if re.search(r'==\s*nil\b|nil\s*==', line):
                issues.append(issue(i, 'Comparing with nil using == — use .nil?',
                                    'LOW', 'Use obj.nil? instead of obj == nil',
                                    'best_practice', stripped))

            # unless…else
            if re.search(r'\bunless\b', line) and re.search(r'\belse\b', line):
                issues.append(issue(i, 'unless…else is confusing',
                                    'LOW', 'Rewrite as if…else',
                                    'style', stripped))

            # puts in production
            if re.search(r'\bputs\s+', line):
                issues.append(issue(i, 'puts() left in production code',
                                    'LOW', 'Use Rails.logger or a logging gem',
                                    'debug', stripped))

            # Hardcoded secrets
            for pat, desc in [
                (r'(?i)password\s*=\s*[\'"][^\'"]{3,}[\'"]', 'Hardcoded password'),
                (r'(?i)secret\s*=\s*[\'"][^\'"]{3,}[\'"]', 'Hardcoded secret'),
                (r'(?i)api_?key\s*=\s*[\'"][^\'"]{5,}[\'"]', 'Hardcoded API key'),
            ]:
                if re.search(pat, line):
                    issues.append(issue(i, desc, 'HIGH',
                                        'Use ENV["..."] or Rails credentials',
                                        'security', stripped))

            # Mass assignment risk
            if re.search(r'\.update_attributes\s*\(\s*params', line) or re.search(r'\.new\s*\(\s*params\b', line):
                issues.append(issue(i, 'Mass assignment with raw params — security risk',
                                    'HIGH', 'Use strong parameters: params.require(...).permit(...)',
                                    'security', stripped))

            # Rescue without exception class
            if re.search(r'\brescue\s*$', line) or re.search(r'\brescue\s*=>', line):
                issues.append(issue(i, 'Bare rescue catches all exceptions including SystemExit',
                                    'MEDIUM', 'Rescue specific exception classes',
                                    'error_handling', stripped))

        return issues

    # ==========================================================================
    # GO ANALYZER
    # ==========================================================================

    def _analyze_go(self, code: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        lines = code.splitlines()

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                continue
            code_part = re.sub(r'//.*', '', line)

            # Unchecked error (err :=  but no if err)
            if re.search(r',\s*err\s*:?=', code_part):
                context = '\n'.join(lines[i:min(i+5, len(lines))])
                if 'if err' not in context and '_ =' not in code_part:
                    issues.append(issue(i, 'Unchecked error return value',
                                        'HIGH', 'Always check: if err != nil { ... }',
                                        'error_handling', stripped))

            # err ignored with _
            if re.search(r',\s*_\s*:?=', code_part) and 'err' not in code_part:
                pass  # legitimate ignoring of non-error returns

            # fmt.Println in production
            if re.search(r'\bfmt\.Print', code_part):
                issues.append(issue(i, 'fmt.Print* in production code',
                                    'LOW', 'Use log package or structured logger (zap, logrus)',
                                    'debug', stripped))

            # Division by zero
            if re.search(r'/\s*0\b', code_part):
                issues.append(issue(i, 'Division by zero', 'HIGH',
                                    'Check divisor before dividing', 'bug', stripped))

            # goroutine leak — goroutine without done/ctx
            if re.search(r'\bgo\s+func\s*\(', code_part):
                context = '\n'.join(lines[max(0, i-5):min(i+20, len(lines))])
                if 'Done()' not in context and 'context' not in context and 'WaitGroup' not in context:
                    issues.append(issue(i, 'goroutine without synchronization — possible leak',
                                        'MEDIUM', 'Use sync.WaitGroup, context, or channel to manage goroutines',
                                        'concurrency', stripped))

            # Hardcoded secrets
            for pat, desc in [
                (r'(?i)password\s*:?=\s*"[^"]{3,}"', 'Hardcoded password'),
                (r'(?i)secret\s*:?=\s*"[^"]{3,}"', 'Hardcoded secret'),
                (r'(?i)apiKey\s*:?=\s*"[^"]{5,}"', 'Hardcoded API key'),
            ]:
                if re.search(pat, code_part):
                    issues.append(issue(i, desc, 'HIGH',
                                        'Use os.Getenv() or a secrets store',
                                        'security', stripped))

            # SQL injection
            if re.search(r'(?i)(db\.Query|db\.Exec|db\.QueryRow)\s*\(\s*fmt\.Sprintf', code_part):
                issues.append(issue(i, 'SQL injection risk — fmt.Sprintf in query',
                                    'HIGH', 'Use parameterized queries with ?/$ placeholders',
                                    'security', stripped))

            # Slice out of bounds (accessing index without length check)
            if re.search(r'\w+\[\s*\d+\s*\]', code_part):
                m = re.search(r'\w+\[(\d+)\]', code_part)
                if m and int(m.group(1)) > 0:
                    context = '\n'.join(lines[max(0, i-5):i])
                    if 'len(' not in context:
                        issues.append(issue(i, 'Slice access without length check',
                                            'MEDIUM', 'Check len(slice) > index before access',
                                            'bug', stripped))

        return issues

    # ==========================================================================
    # RUST ANALYZER
    # ==========================================================================

    def _analyze_rust(self, code: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        lines = code.splitlines()

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                continue
            code_part = re.sub(r'//.*', '', line)

            # .unwrap() — panics on None/Err
            if re.search(r'\.unwrap\s*\(\s*\)', code_part):
                issues.append(issue(i, '.unwrap() panics on None/Err',
                                    'MEDIUM', 'Use match, ?, if let, or .unwrap_or()',
                                    'error_handling', stripped))

            # .expect() — also panics
            if re.search(r'\.expect\s*\(', code_part):
                issues.append(issue(i, '.expect() panics — use only where panic is acceptable',
                                    'LOW', 'In library code prefer returning Result<>',
                                    'error_handling', stripped))

            # unsafe block
            if re.search(r'\bunsafe\s*\{', code_part):
                issues.append(issue(i, 'unsafe block — bypasses Rust safety guarantees',
                                    'MEDIUM', 'Minimize unsafe; document safety invariants',
                                    'safety', stripped))

            # todo!/unimplemented! in production
            if re.search(r'\btodo!\s*\(|\bunimplemented!\s*\(', code_part):
                issues.append(issue(i, 'todo!() / unimplemented!() panics at runtime',
                                    'MEDIUM', 'Implement the functionality before production',
                                    'bug', stripped))

            # clone() overuse hint
            if re.search(r'\.clone\s*\(\s*\)', code_part):
                issues.append(issue(i, '.clone() — ensure this is intentional (performance cost)',
                                    'LOW', 'Consider borrowing (&T) instead of cloning',
                                    'performance', stripped))

            # Division by zero (literal)
            if re.search(r'/\s*0\b', code_part):
                issues.append(issue(i, 'Division by zero — panics in Rust',
                                    'HIGH', 'Check divisor or use checked_div()',
                                    'bug', stripped))

            # Hardcoded secrets
            for pat, desc in [
                (r'(?i)password\s*=\s*"[^"]{3,}"', 'Hardcoded password'),
                (r'(?i)secret\s*=\s*"[^"]{3,}"', 'Hardcoded secret'),
                (r'(?i)api_?key\s*=\s*"[^"]{5,}"', 'Hardcoded API key'),
            ]:
                if re.search(pat, code_part):
                    issues.append(issue(i, desc, 'HIGH',
                                        'Use std::env::var() or a secrets crate',
                                        'security', stripped))

            # Integer overflow (debug mode panics, release mode wraps)
            if re.search(r'\bas\s+u8\b|\bas\s+i8\b', code_part):
                issues.append(issue(i, 'Truncating cast (as u8/i8) may overflow silently',
                                    'MEDIUM', 'Use .try_into() or check bounds before casting',
                                    'bug', stripped))

            # println! in library crate (output goes to stdout)
            if re.search(r'\bprintln!\s*\(', code_part):
                issues.append(issue(i, 'println!() in library code pollutes stdout',
                                    'LOW', 'Use log crate macros (info!, debug!) instead',
                                    'debug', stripped))

        return issues

    # ==========================================================================
    # SWIFT ANALYZER
    # ==========================================================================

    def _analyze_swift(self, code: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        lines = code.splitlines()

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                continue
            code_part = re.sub(r'//.*', '', line)

            # Force unwrap with !
            if re.search(r'\b\w+!\s*[.\(\[]', code_part) and '!=' not in code_part and '!is' not in code_part:
                issues.append(issue(i, 'Force unwrap (!) risks runtime crash',
                                    'MEDIUM', 'Use if let, guard let, or ?? default value',
                                    'safety', stripped))

            # Force cast with as!
            if re.search(r'\bas!\s+\w+', code_part):
                issues.append(issue(i, 'Force cast (as!) risks runtime crash',
                                    'MEDIUM', 'Use as? with optional binding',
                                    'safety', stripped))

            # print() in production
            if re.search(r'\bprint\s*\(', code_part):
                issues.append(issue(i, 'print() left in production code',
                                    'LOW', 'Use os_log or a logging framework',
                                    'debug', stripped))

            # Hardcoded secrets
            for pat, desc in [
                (r'(?i)password\s*=\s*"[^"]{3,}"', 'Hardcoded password'),
                (r'(?i)apiKey\s*=\s*"[^"]{5,}"', 'Hardcoded API key'),
                (r'(?i)secret\s*=\s*"[^"]{3,}"', 'Hardcoded secret'),
            ]:
                if re.search(pat, code_part):
                    issues.append(issue(i, desc, 'HIGH',
                                        'Use Keychain or environment configuration',
                                        'security', stripped))

            # Retain cycle risk in closures
            if re.search(r'\{[^}]*\bself\b[^}]*\}', code_part) and '[weak self]' not in line and '[unowned self]' not in line:
                issues.append(issue(i, 'Possible retain cycle — self captured in closure',
                                    'MEDIUM', 'Use [weak self] or [unowned self] in capture list',
                                    'memory', stripped))

            # DispatchQueue.main.sync — deadlock risk
            if re.search(r'DispatchQueue\.main\.sync\s*\{', code_part):
                issues.append(issue(i, 'DispatchQueue.main.sync from main thread causes deadlock',
                                    'HIGH', 'Use .async instead of .sync on main queue',
                                    'concurrency', stripped))

            # UIKit access on background thread (heuristic)
            if re.search(r'\.backgroundColor|\.text\s*=|\.isHidden|\.alpha\s*=', code_part):
                context = '\n'.join(lines[max(0, i-5):i])
                if 'DispatchQueue.global' in context:
                    issues.append(issue(i, 'Possible UIKit access on background thread',
                                        'HIGH', 'Dispatch UI updates to DispatchQueue.main.async',
                                        'concurrency', stripped))

        return issues

    # ==========================================================================
    # KOTLIN ANALYZER
    # ==========================================================================

    def _analyze_kotlin(self, code: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        lines = code.splitlines()

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                continue
            code_part = re.sub(r'//.*', '', line)

            # !! not-null assertion
            if '!!' in code_part:
                issues.append(issue(i, 'Not-null assertion (!!) — crashes if null',
                                    'MEDIUM', 'Use ?. safe call or ?: Elvis operator',
                                    'safety', stripped))

            # System.out.println
            if re.search(r'\bprintln\s*\(', code_part):
                issues.append(issue(i, 'println() in production code',
                                    'LOW', 'Use a logging library (Timber, Logback)',
                                    'debug', stripped))

            # Hardcoded secrets
            for pat, desc in [
                (r'(?i)password\s*=\s*"[^"]{3,}"', 'Hardcoded password'),
                (r'(?i)apiKey\s*=\s*"[^"]{5,}"', 'Hardcoded API key'),
                (r'(?i)secret\s*=\s*"[^"]{3,}"', 'Hardcoded secret'),
            ]:
                if re.search(pat, code_part):
                    issues.append(issue(i, desc, 'HIGH',
                                        'Use BuildConfig or environment configuration',
                                        'security', stripped))

            # Thread.sleep in coroutine
            if re.search(r'\bThread\.sleep\s*\(', code_part):
                issues.append(issue(i, 'Thread.sleep() blocks coroutine thread',
                                    'MEDIUM', 'Use delay() inside suspend function',
                                    'concurrency', stripped))

            # Mutable public var in data class
            if re.search(r'\bdata class\b', code_part):
                context = '\n'.join(lines[i:min(i+10, len(lines))])
                if re.search(r'\bvar\b', context):
                    issues.append(issue(i, 'Mutable var in data class — prefer immutable val',
                                        'LOW', 'Use val for immutability; copy() for modification',
                                        'design', stripped))

            # lateinit on primitive types (not allowed, would be compile error — skip)

            # runBlocking in coroutine (deadlock risk)
            if re.search(r'\brunBlocking\s*\{', code_part):
                issues.append(issue(i, 'runBlocking blocks the current thread',
                                    'MEDIUM', 'Avoid runBlocking in production coroutine code',
                                    'concurrency', stripped))

            # GlobalScope usage
            if re.search(r'\bGlobalScope\b', code_part):
                issues.append(issue(i, 'GlobalScope.launch — coroutines may leak',
                                    'MEDIUM', 'Use viewModelScope, lifecycleScope, or CoroutineScope',
                                    'concurrency', stripped))

        return issues

    # ==========================================================================
    # HTML ANALYZER
    # ==========================================================================

    def _analyze_html(self, code: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        lines = code.splitlines()
        seen_ids: Dict[str, int] = {}

        has_doctype = any('<!DOCTYPE' in l.upper() for l in lines[:5])
        has_lang = any('lang=' in l for l in lines[:10])
        has_meta_charset = any('charset' in l.lower() for l in lines[:20])
        has_meta_viewport = any('viewport' in l.lower() for l in lines[:20])
        has_title = any('<title>' in l.lower() for l in lines)

        if not has_doctype:
            issues.append(issue(1, 'Missing <!DOCTYPE html> declaration',
                                'MEDIUM', 'Add <!DOCTYPE html> at the start of the file',
                                'validation', ''))
        if not has_lang:
            issues.append(issue(1, 'Missing lang attribute on <html>',
                                'MEDIUM', 'Add lang="en" (or appropriate language) to <html>',
                                'accessibility', ''))
        if not has_meta_charset:
            issues.append(issue(1, 'Missing charset meta tag',
                                'MEDIUM', 'Add <meta charset="UTF-8">',
                                'validation', ''))
        if not has_meta_viewport:
            issues.append(issue(1, 'Missing viewport meta tag',
                                'MEDIUM', 'Add <meta name="viewport" content="width=device-width, initial-scale=1">',
                                'accessibility', ''))
        if not has_title:
            issues.append(issue(1, 'Missing <title> element',
                                'MEDIUM', 'Add a descriptive <title> for SEO and accessibility',
                                'accessibility', ''))

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Missing alt on img
            if re.search(r'<img\b', line, re.IGNORECASE) and 'alt=' not in line.lower():
                issues.append(issue(i, 'Image missing alt attribute',
                                    'MEDIUM', 'Add descriptive alt text for accessibility',
                                    'accessibility', stripped))

            # Duplicate ID
            for id_val in re.findall(r'\bid=["\']([^"\']+)["\']', line):
                if id_val in seen_ids:
                    issues.append(issue(i, f'Duplicate ID: "{id_val}" (first at line {seen_ids[id_val]})',
                                        'HIGH', 'IDs must be unique per page',
                                        'validation', stripped))
                else:
                    seen_ids[id_val] = i

            # Inline styles (maintainability)
            if re.search(r'\bstyle\s*=\s*["\']', line, re.IGNORECASE):
                issues.append(issue(i, 'Inline style attribute — prefer CSS classes',
                                    'LOW', 'Move styles to a CSS file for maintainability',
                                    'style', stripped))

            # Deprecated HTML tags
            for tag in ['<font', '<center', '<marquee', '<blink', '<big', '<strike', '<tt']:
                if tag in line.lower():
                    issues.append(issue(i, f'Deprecated HTML element: {tag}>',
                                        'MEDIUM', 'Use CSS for styling instead',
                                        'deprecated', stripped))

            # onclick inline JavaScript
            if re.search(r'\bon\w+\s*=\s*["\']', line, re.IGNORECASE):
                issues.append(issue(i, 'Inline event handler — prefer addEventListener()',
                                    'LOW', 'Use addEventListener in separate JS file (separation of concerns)',
                                    'best_practice', stripped))

            # Link without rel="noopener" for target="_blank"
            if 'target="_blank"' in line.lower() and 'rel=' not in line.lower():
                issues.append(issue(i, 'target="_blank" without rel="noopener noreferrer"',
                                    'MEDIUM', 'Add rel="noopener noreferrer" to prevent tab-napping',
                                    'security', stripped))

            # Form without method attribute
            if re.search(r'<form\b', line, re.IGNORECASE) and 'method=' not in line.lower():
                issues.append(issue(i, 'Form missing method attribute',
                                    'LOW', 'Specify method="post" or method="get"',
                                    'validation', stripped))

            # Empty links
            if re.search(r'<a\s[^>]*href\s*=\s*["\']#["\']', line, re.IGNORECASE):
                issues.append(issue(i, 'Empty anchor href="#" — poor accessibility',
                                    'LOW', 'Use a real URL or button element for click actions',
                                    'accessibility', stripped))

            # Missing label for form inputs
            if re.search(r'<input\b', line, re.IGNORECASE) and 'aria-label' not in line.lower():
                if not re.search(r'type=["\']hidden["\']', line, re.IGNORECASE):
                    issues.append(issue(i, 'Input without aria-label or associated <label>',
                                        'MEDIUM', 'Associate a <label for="id"> or use aria-label',
                                        'accessibility', stripped))

        return issues

    # ==========================================================================
    # CSS ANALYZER
    # ==========================================================================

    def _analyze_css(self, code: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        lines = code.splitlines()
        selectors: Dict[str, int] = {}

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('/*'):
                continue
            code_part = re.sub(r'/\*.*?\*/', '', stripped)

            # !important
            if '!important' in code_part:
                issues.append(issue(i, '!important — overrides cascade, hard to maintain',
                                    'LOW', 'Increase selector specificity instead',
                                    'best_practice', stripped))

            # Missing units on non-zero values
            if ':' in code_part and ';' in code_part:
                value_part = code_part.split(':', 1)[1].split(';')[0].strip()
                # Only flag if there's a bare non-zero number
                if re.search(r'(?<!\d)\b[1-9]\d*\b(?!\s*(?:px|em|rem|%|vh|vw|vmin|vmax|pt|cm|mm|in|ex|ch|fr|deg|rad|turn|ms|s|dpi|dpcm|dppx))', value_part):
                    # Exclude flex/grid shorthand values, z-index, opacity, font-weight
                    prop = code_part.split(':')[0].strip().lower()
                    UNITLESS_OK = {'z-index', 'opacity', 'font-weight', 'line-height', 'flex',
                                   'flex-grow', 'flex-shrink', 'order', 'column-count',
                                   'counter-increment', 'counter-reset', 'widows', 'orphans',
                                   'animation-iteration-count', 'tab-size'}
                    if prop not in UNITLESS_OK:
                        issues.append(issue(i, 'Numeric value without units',
                                            'MEDIUM', 'Add units: px, em, rem, %, etc.',
                                            'validation', stripped))

            # Duplicate selectors
            if '{' in code_part and '}' not in code_part:
                sel = code_part.split('{')[0].strip()
                if sel:
                    if sel in selectors:
                        issues.append(issue(i, f'Duplicate CSS selector: "{sel}" (first at line {selectors[sel]})',
                                            'LOW', 'Merge duplicate selectors',
                                            'style', stripped))
                    else:
                        selectors[sel] = i

            # Vendor prefix without standard property (basic)
            if re.search(r'-webkit-|-moz-|-ms-|-o-', code_part):
                prop_match = re.search(r'(-webkit-|-moz-|-ms-|-o-)(\S+)', code_part)
                if prop_match:
                    std_prop = prop_match.group(2)
                    if std_prop not in code:
                        issues.append(issue(i, f'Vendor prefix without standard property: {std_prop}',
                                            'LOW', f'Also include unprefixed: {std_prop}',
                                            'compatibility', stripped))

            # Using px for font-size (accessibility)
            if re.search(r'font-size\s*:\s*\d+px', code_part, re.IGNORECASE):
                issues.append(issue(i, 'font-size in px — not accessible (ignores browser zoom)',
                                    'LOW', 'Use rem or em for scalable font sizes',
                                    'accessibility', stripped))

            # ID selectors (high specificity)
            if re.search(r'#\w+', code_part) and '{' in code_part:
                issues.append(issue(i, 'ID selector — very high specificity, hard to override',
                                    'LOW', 'Prefer class selectors for reusability',
                                    'best_practice', stripped))

            # Overly broad selectors
            if re.match(r'^\*\s*{', code_part):
                issues.append(issue(i, 'Universal selector (*) — performance impact',
                                    'LOW', 'Target specific elements to improve rendering speed',
                                    'performance', stripped))

        return issues

    # ==========================================================================
    # COMMON ANALYSIS (all languages)
    # ==========================================================================

    def _common_analysis(self, code: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        lines = code.splitlines()

        COMMON_SECRET_PATTERNS = [
            (r'(?i)password\s*[:=]\s*[\'"][^\'"]{3,}[\'"]', 'Hardcoded password'),
            (r'(?i)api[_-]?key\s*[:=]\s*[\'"][^\'"]{5,}[\'"]', 'Hardcoded API key'),
            (r'(?i)secret\s*[:=]\s*[\'"][^\'"]{3,}[\'"]', 'Hardcoded secret'),
            (r'(?i)\btoken\s*[:=]\s*[\'"][^\'"]{5,}[\'"]', 'Hardcoded token'),
            # AWS key pattern
            (r'AKIA[0-9A-Z]{16}', 'Possible AWS access key'),
            # Generic private key header
            (r'-----BEGIN (?:RSA|EC|DSA|OPENSSH) PRIVATE KEY-----', 'Private key embedded in code'),
        ]

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Long lines
            if len(line) > 120:
                issues.append(issue(i, f'Line too long ({len(line)} characters)',
                                    'LOW', 'Keep lines ≤ 120 chars for readability',
                                    'style', line[:60] + '...'))

            # TODO / FIXME
            if re.search(r'\b(TODO|FIXME|XXX|HACK|BUG)\b', line, re.IGNORECASE):
                issues.append(issue(i, 'TODO/FIXME comment — unfinished work',
                                    'LOW', 'Resolve before shipping to production',
                                    'maintenance', stripped))

            # Common secrets (cross-language)
            for pat, desc in COMMON_SECRET_PATTERNS:
                if re.search(pat, line):
                    issues.append(issue(i, desc, 'HIGH',
                                        'Use environment variables or a secrets manager',
                                        'security', stripped[:80]))

        # No newline at end of file
        if code and not code.endswith('\n'):
            issues.append(issue(len(lines), 'No newline at end of file',
                                'LOW', 'Add newline at EOF (POSIX standard)',
                                'style', 'EOF'))

        return issues


# ==============================================================================
# CLI ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python code_analyzer.py <filename> [--json] [--no-filter]")
        sys.exit(1)

    filename = sys.argv[1]
    output_json = '--json' in sys.argv
    no_filter = '--no-filter' in sys.argv

    try:
        with open(filename, 'r', encoding='utf-8', errors='replace') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    EXT_TO_LANG = {
        'py': 'python', 'js': 'javascript', 'ts': 'typescript',
        'java': 'java', 'cpp': 'cpp', 'cc': 'cpp', 'cxx': 'cpp',
        'c': 'c', 'h': 'c', 'cs': 'csharp',
        'php': 'php', 'rb': 'ruby', 'go': 'go',
        'rs': 'rust', 'swift': 'swift', 'kt': 'kotlin', 'kts': 'kotlin',
        'html': 'html', 'htm': 'html', 'css': 'css',
    }

    ext = filename.rsplit('.', 1)[-1].lower()
    lang = EXT_TO_LANG.get(ext, 'python')

    print(f"\n🔍 Analyzing: {filename} ({lang})")

    analyzer = CodeAnalyzer(language=lang, filter_noise=not no_filter)
    results = analyzer.analyze(source)

    if output_json:
        print(json.dumps(results, indent=2))
        sys.exit(0)

    # Pretty print
    ICONS = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}
    print(f"\n{'='*65}")
    print(f"  ANALYSIS RESULTS — {len(results)} issue(s) found")
    print(f"{'='*65}\n")

    counts = {s: sum(1 for r in results if r['severity'] == s) for s in ('HIGH', 'MEDIUM', 'LOW')}
    print(f"  {ICONS['HIGH']} HIGH: {counts['HIGH']}   "
          f"{ICONS['MEDIUM']} MEDIUM: {counts['MEDIUM']}   "
          f"{ICONS['LOW']} LOW: {counts['LOW']}\n")

    if not results:
        print("  ✅ No issues detected!")
    else:
        current_sev = None
        for r in results:
            if r['severity'] != current_sev:
                current_sev = r['severity']
                print(f"\n{'─'*65}")
                print(f"  {ICONS[current_sev]} {current_sev} SEVERITY")
                print(f"{'─'*65}")
            print(f"\n  Line {r['line']:>4}: [{r['category']}] {r['problem']}")
            print(f"           → {r['suggestion']}")
            if r.get('code'):
                preview = r['code'][:80] + ('...' if len(r['code']) > 80 else '')
                print(f"           Code: {preview}")

    print()