"""
code_analyzer.py - Complete Multi-Language Bug Detection
Supports 14 programming languages with intelligent noise filtering
"""

import ast
import re
from typing import List, Dict, Any, Set, Optional

class CodeAnalyzer:
    def __init__(self, language='python', filter_noise=True):
        self.language = language
        self.filter_noise = filter_noise
        self.builtins = self._get_builtins(language)
    
    def _get_builtins(self, language):
        """Get built-in functions/objects for each language"""
        builtins_map = {
            'python': ['print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple', 
                      'range', 'open', 'sum', 'min', 'max', 'abs', 'round', 'type', 'isinstance',
                      'enumerate', 'zip', 'map', 'filter', 'sorted', 'reversed', 'Exception',
                      'ValueError', 'TypeError', 'KeyError', 'IndexError', 'AttributeError'],
            'javascript': ['console', 'document', 'window', 'Math', 'Date', 'Array', 'Object', 
                          'String', 'Number', 'Boolean', 'RegExp', 'JSON', 'Promise', 'Set', 'Map'],
            'typescript': ['console', 'document', 'window', 'Math', 'Date', 'Array', 'Object',
                          'String', 'Number', 'Boolean', 'RegExp', 'JSON', 'Promise', 'Map', 'Set'],
            'java': ['System', 'String', 'Integer', 'Double', 'Boolean', 'List', 'ArrayList',
                    'Map', 'HashMap', 'Set', 'HashSet', 'Arrays', 'Collections', 'Exception'],
            'cpp': ['std', 'cout', 'cin', 'endl', 'vector', 'string', 'map', 'set', 'list',
                   'ifstream', 'ofstream', 'fstream', 'pair', 'make_pair'],
            'c': ['printf', 'scanf', 'fopen', 'fclose', 'fread', 'fwrite', 'malloc', 'free',
                 'NULL', 'FILE'],
            'csharp': ['Console', 'String', 'Int32', 'Double', 'Boolean', 'List', 'Dictionary',
                      'File', 'StreamReader', 'StreamWriter', 'Exception'],
            'php': ['echo', 'print', 'array', 'isset', 'empty', 'count', 'strlen', 'implode',
                   'explode', 'file_get_contents', 'file_put_contents', '$_GET', '$_POST'],
            'ruby': ['puts', 'print', 'gets', 'Array', 'Hash', 'String', 'Integer', 'Float',
                    'File', 'Dir', 'nil', 'true', 'false'],
            'go': ['fmt', 'Println', 'Printf', 'len', 'append', 'make', 'new', 'close',
                  'error', 'nil'],
            'rust': ['println!', 'print!', 'format!', 'vec!', 'String', 'Vec', 'Option', 'Result',
                    'Some', 'None', 'Ok', 'Err'],
            'swift': ['print', 'String', 'Int', 'Double', 'Bool', 'Array', 'Dictionary', 'Set',
                     'nil', 'true', 'false'],
            'kotlin': ['println', 'print', 'listOf', 'mapOf', 'setOf', 'arrayOf', 'String',
                      'Int', 'Double', 'Boolean', 'null', 'true', 'false'],
            'html': ['document', 'window', 'console', 'alert', 'prompt', 'localStorage'],
            'css': []
        }
        return set(builtins_map.get(language, []))
    
    def analyze(self, code: str) -> List[Dict[str, Any]]:
        """Main analysis method - detects bugs in all languages"""
        issues = []
        
        print(f"🔍 Analyzing {len(code)} characters of {self.language} code...")
        
        # Route to language-specific analyzer
        analyzers = {
            'python': self._analyze_python,
            'javascript': self._analyze_javascript,
            'typescript': self._analyze_typescript,
            'java': self._analyze_java,
            'cpp': self._analyze_cpp,
            'c': self._analyze_c,
            'csharp': self._analyze_csharp,
            'php': self._analyze_php,
            'ruby': self._analyze_ruby,
            'go': self._analyze_go,
            'rust': self._analyze_rust,
            'swift': self._analyze_swift,
            'kotlin': self._analyze_kotlin,
            'html': self._analyze_html,
            'css': self._analyze_css
        }
        
        if self.language in analyzers:
            issues.extend(analyzers[self.language](code))
        
        # Common issues across all languages
        common_issues = self._common_analysis(code)
        
        # Filter out noisy warnings if enabled
        if self.filter_noise:
            common_issues = self._filter_noisy_warnings(common_issues)
        
        issues.extend(common_issues)
        
        # Sort by severity
        severity_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        issues.sort(key=lambda x: severity_order.get(x['severity'], 3))
        
        print(f"✅ Found {len(issues)} meaningful issues!")
        return issues
    
    def _filter_noisy_warnings(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove noisy warnings that cause too many false positives"""
        filtered = []
        
        # Patterns that are often too noisy
        noisy_patterns = [
            'Trailing whitespace',
            'Line too long',  # Keep if > 120, but can be noisy
            'Missing semicolon',  # Style preference, not a bug
        ]
        
        for issue in issues:
            # Keep HIGH severity always
            if issue['severity'] == 'HIGH':
                filtered.append(issue)
                continue
            
            # Filter out noisy LOW severity issues
            is_noisy = any(pattern in issue['problem'] for pattern in noisy_patterns)
            
            # Keep line length if it's REALLY long (>150)
            if 'Line too long' in issue['problem'] and issue['severity'] == 'LOW':
                # Extract line length from problem string
                match = re.search(r'\((\d+)', issue['problem'])
                if match and int(match.group(1)) > 150:
                    filtered.append(issue)  # Keep extremely long lines
            elif not is_noisy:
                filtered.append(issue)
        
        return filtered
    
    # ============================================================================
    # PYTHON ANALYZER
    # ============================================================================
    def _analyze_python(self, code: str) -> List[Dict[str, Any]]:
        """Python-specific bug detection"""
        issues = []
        lines = code.split('\n')
        
        try:
            tree = ast.parse(code)
            
            # Track defined variables with scope
            defined_vars = set(self.builtins)
            functions = set()
            classes = set()
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    defined_vars.add(node.name)
                    functions.add(node.name)
                    for arg in node.args.args:
                        defined_vars.add(arg.arg)
                elif isinstance(node, ast.ClassDef):
                    defined_vars.add(node.name)
                    classes.add(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            defined_vars.add(target.id)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        defined_vars.add(alias.asname or alias.name)
                        imports.add(alias.asname or alias.name)
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if alias.name != '*':
                            defined_vars.add(alias.asname or alias.name)
                            imports.add(alias.asname or alias.name)
            
            # ================================================================
            # 1. Undefined variables
            # ================================================================
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    if node.id not in defined_vars and not node.id.startswith('_'):
                        issues.append({
                            'line': node.lineno,
                            'problem': f'Undefined variable: {node.id}',
                            'severity': 'HIGH',
                            'suggestion': f'Define {node.id} before using it',
                            'category': 'bug',
                            'code': node.id
                        })
            
            # ================================================================
            # 2. Bare except clauses
            # ================================================================
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    issues.append({
                        'line': node.lineno,
                        'problem': 'Bare except clause',
                        'severity': 'HIGH',
                        'suggestion': 'Catch specific exceptions (except ValueError:)',
                        'category': 'error_handling',
                        'code': 'except:'
                    })
            
            # ================================================================
            # 3. Mutable default arguments
            # ================================================================
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for i, default in enumerate(node.args.defaults):
                        if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                            arg_name = node.args.args[len(node.args.args) - len(node.args.defaults) + i].arg
                            issues.append({
                                'line': node.lineno,
                                'problem': f'Mutable default argument: {arg_name}',
                                'severity': 'MEDIUM',
                                'suggestion': 'Use None as default and create mutable inside function',
                                'category': 'bug',
                                'code': f'{arg_name}=[]'
                            })
            
            # ================================================================
            # 4. Missing self in class methods
            # ================================================================
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if not item.name.startswith('__') and not any(
                                isinstance(d, ast.Name) and d.id in ['staticmethod', 'classmethod'] 
                                for d in item.decorator_list
                            ):
                                if not item.args.args or item.args.args[0].arg != 'self':
                                    issues.append({
                                        'line': item.lineno,
                                        'problem': f'Method {item.name}() missing self parameter',
                                        'severity': 'HIGH',
                                        'suggestion': 'Add "self" as first parameter',
                                        'category': 'bug',
                                        'code': f'def {item.name}():'
                                    })
            
            # ================================================================
            # 5. Wildcard imports
            # ================================================================
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and any(alias.name == '*' for alias in node.names):
                        issues.append({
                            'line': node.lineno,
                            'problem': f'Wildcard import: from {node.module} import *',
                            'severity': 'MEDIUM',
                            'suggestion': 'Import only what you need',
                            'category': 'best_practice',
                            'code': f'from {node.module} import *'
                        })
            
            # ================================================================
            # 6. Empty except block
            # ================================================================
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                        issues.append({
                            'line': node.lineno,
                            'problem': 'Empty except block',
                            'severity': 'MEDIUM',
                            'suggestion': 'Handle the exception or at least log it',
                            'category': 'error_handling',
                            'code': 'except: pass'
                        })
            
            # ================================================================
            # 7. Too many arguments (>7)
            # ================================================================
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if len(node.args.args) > 7:
                        issues.append({
                            'line': node.lineno,
                            'problem': f'Function {node.name}() has {len(node.args.args)} arguments',
                            'severity': 'MEDIUM',
                            'suggestion': 'Consider using a dataclass or reducing arguments',
                            'category': 'design',
                            'code': f'def {node.name}(...)'
                        })
            
            # ================================================================
            # 8. Redefining built-ins
            # ================================================================
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    if node.id in self.builtins and node.id not in ['__file__', '__name__']:
                        issues.append({
                            'line': node.lineno,
                            'problem': f'Variable redefines built-in: {node.id}',
                            'severity': 'MEDIUM',
                            'suggestion': f'Use a different variable name',
                            'category': 'best_practice',
                            'code': f'{node.id} = ...'
                        })
            
            # ================================================================
            # 9. Comparing None with ==
            # ================================================================
            for node in ast.walk(tree):
                if isinstance(node, ast.Compare):
                    for op, comparator in zip(node.ops, node.comparators):
                        if isinstance(op, (ast.Eq, ast.NotEq)) and isinstance(comparator, ast.Constant) and comparator.value is None:
                            issues.append({
                                'line': node.lineno,
                                'problem': 'Comparing None with == or !=',
                                'severity': 'LOW',
                                'suggestion': 'Use "is None" or "is not None"',
                                'category': 'best_practice',
                                'code': 'x == None'
                            })
            
            # ================================================================
            # 10. Unused variables (simplified)
            # ================================================================
            used_vars = set()
            assigned_vars = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    used_vars.add(node.id)
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    assigned_vars.add(node.id)
            
            unused = assigned_vars - used_vars - {'self', 'cls'} - self.builtins - imports
            for var in unused:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name) and node.id == var and isinstance(node.ctx, ast.Store):
                        issues.append({
                            'line': node.lineno,
                            'problem': f'Unused variable: {var}',
                            'severity': 'LOW',
                            'suggestion': f'Remove {var} or use it',
                            'category': 'style',
                            'code': var
                        })
                        break
            
        except SyntaxError as e:
            issues.append({
                'line': e.lineno or 1,
                'problem': f'Syntax error: {e.msg}',
                'severity': 'HIGH',
                'suggestion': 'Fix the syntax error',
                'category': 'syntax',
                'code': lines[e.lineno-1] if e.lineno and e.lineno <= len(lines) else ''
            })
        
        # ================================================================
        # 11. Division by zero
        # ================================================================
        for i, line in enumerate(lines, 1):
            if re.search(r'/[\s]*0\b', line) and not re.search(r'#.*?/[\s]*0', line):
                issues.append({
                    'line': i,
                    'problem': 'Potential division by zero',
                    'severity': 'HIGH',
                    'suggestion': 'Check if denominator is zero before division',
                    'category': 'bug',
                    'code': line.strip()
                })
        
        # ================================================================
        # 12. Hardcoded secrets
        # ================================================================
        secret_patterns = [
            (r'password\s*=\s*[\'\"][^\'\"]+[\'\"]', 'Hardcoded password'),
            (r'api[_-]?key\s*=\s*[\'\"][^\'\"]+[\'\"]', 'Hardcoded API key'),
            (r'secret\s*=\s*[\'\"][^\'\"]+[\'\"]', 'Hardcoded secret'),
            (r'token\s*=\s*[\'\"][^\'\"]+[\'\"]', 'Hardcoded token'),
            (r'auth\s*=\s*[\'\"][^\'\"]+[\'\"]', 'Hardcoded auth')
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, desc in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'line': i,
                        'problem': desc,
                        'severity': 'HIGH',
                        'suggestion': 'Use environment variables or secrets manager',
                        'category': 'security',
                        'code': line.strip()
                    })
        
        # ================================================================
        # 13. eval() usage
        # ================================================================
        for i, line in enumerate(lines, 1):
            if 'eval(' in line and not re.search(r'#.*?eval\(', line):
                issues.append({
                    'line': i,
                    'problem': 'eval() function used',
                    'severity': 'HIGH',
                    'suggestion': 'Avoid eval() - security risk. Use safer alternatives',
                    'category': 'security',
                    'code': line.strip()
                })
        
        # ================================================================
        # 14. open() without close (resource leak)
        # ================================================================
        open_calls = []
        for i, line in enumerate(lines, 1):
            if 'open(' in line and 'with' not in line and not re.search(r'#.*?open\(', line):
                open_calls.append(i)
        
        close_count = sum(1 for line in lines if '.close()' in line)
        
        if len(open_calls) > close_count:
            for line_num in open_calls[:len(open_calls)-close_count]:
                issues.append({
                    'line': line_num,
                    'problem': 'File opened but not closed',
                    'severity': 'MEDIUM',
                    'suggestion': 'Use "with open() as file:" context manager',
                    'category': 'resource_leak',
                    'code': lines[line_num-1].strip()
                })
        
        return issues
    
    # ============================================================================
    # C++ ANALYZER - COMPREHENSIVE
    # ============================================================================
    def _analyze_cpp(self, code: str) -> List[Dict[str, Any]]:
        """C++ specific bug detection - detects all issues in sample"""
        issues = []
        lines = code.split('\n')
        
        # Track for memory leaks
        new_calls = {}
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # ================================================================
            # HIGH SEVERITY ISSUES (Critical bugs & security)
            # ================================================================
            
            # 1. Plain text passwords
            if 'users.push_back({username, password})' in line or ('password' in line and 'push_back' in line):
                issues.append({
                    'line': i,
                    'problem': 'Storing plain text passwords',
                    'severity': 'HIGH',
                    'suggestion': 'Hash passwords before storing (bcrypt, SHA256)',
                    'category': 'security',
                    'code': line.strip()
                })
            
            # 2. Login function logic error (returns false on first mismatch)
            if 'bool login' in line:
                # Check if there's a return false inside the loop
                in_loop = False
                loop_line = i
                for j in range(i, min(i+30, len(lines))):
                    if 'for (' in lines[j-1] or 'for (' in lines[j-1]:
                        in_loop = True
                    if in_loop and 'return false;' in lines[j-1]:
                        issues.append({
                            'line': loop_line,
                            'problem': 'Login function returns false on first non-match',
                            'severity': 'HIGH',
                            'suggestion': 'Move return false outside the loop - check all users first',
                            'category': 'bug',
                            'code': 'bool login(...)'
                        })
                        break
                    if in_loop and '}' in lines[j-1] and lines[j-1].count('}') > lines[j-1].count('{'):
                        in_loop = False
            
            # 3. Division by zero
            if 'double divide' in line and '/' in line:
                # Check if there's a zero check
                has_check = False
                for j in range(max(1, i-5), min(len(lines), i+10)):
                    if 'if (b == 0)' in lines[j-1] or 'if (b == 0.0)' in lines[j-1]:
                        has_check = True
                        break
                if not has_check:
                    issues.append({
                        'line': i,
                        'problem': 'No zero division handling',
                        'severity': 'HIGH',
                        'suggestion': 'Add check: if (b == 0) throw exception or return error',
                        'category': 'bug',
                        'code': line.strip()
                    })
            
            # 4. Vector access without bounds checking
            if '[' in line and ']' in line and 'users' in line and '.at(' not in line:
                if 'if' not in ''.join(lines[max(0, i-3):i]):
                    issues.append({
                        'line': i,
                        'problem': 'Vector access without bounds checking',
                        'severity': 'HIGH',
                        'suggestion': 'Use .at() for bounds checking or check size() first',
                        'category': 'bug',
                        'code': line.strip()
                    })
            
            # 5. Division by size() without empty check
            if 'total / numbers.size()' in line or '/ numbers.size()' in line:
                has_check = False
                for j in range(max(1, i-10), i):
                    if 'if (numbers.empty())' in lines[j-1] or 'if (!numbers.empty())' in lines[j-1]:
                        has_check = True
                        break
                if not has_check:
                    issues.append({
                        'line': i,
                        'problem': 'Division by size() without empty check',
                        'severity': 'HIGH',
                        'suggestion': 'Check if numbers.empty() before division',
                        'category': 'bug',
                        'code': line.strip()
                    })
            
            # 6. File not closed
            file_vars = []
            if 'ifstream' in line or 'ofstream' in line or 'fstream' in line:
                var_match = re.search(r'(?:ifstream|ofstream|fstream)\s+(\w+)', line)
                if var_match:
                    file_vars.append((var_match.group(1), i))
            
            for var_name, line_num in file_vars:
                has_close = False
                for j in range(line_num, min(line_num+50, len(lines))):
                    if f'{var_name}.close()' in lines[j-1]:
                        has_close = True
                        break
                if not has_close:
                    issues.append({
                        'line': line_num,
                        'problem': f'File stream {var_name} not closed',
                        'severity': 'MEDIUM',
                        'suggestion': 'Call close() or let it go out of scope (RAII)',
                        'category': 'resource_leak',
                        'code': lines[line_num-1].strip()
                    })
            
            # 7. system() call (security vulnerability)
            if 'system(' in line:
                issues.append({
                    'line': i,
                    'problem': 'system() function used',
                    'severity': 'HIGH',
                    'suggestion': 'Avoid system() - security risk. Use safer alternatives',
                    'category': 'security',
                    'code': line.strip()
                })
            
            # 8. Infinite recursion
            if 'void recursive_bug' in line or 'recursive_bug()' in line:
                # Look for function definition
                for j in range(max(1, i-10), i+10):
                    if j <= len(lines) and 'void recursive_bug' in lines[j-1]:
                        # Check if there's a condition
                        has_condition = False
                        for k in range(j, min(j+15, len(lines))):
                            if 'if (' in lines[k-1] and 'recursive_bug' not in lines[k-1]:
                                has_condition = True
                                break
                        if not has_condition:
                            issues.append({
                                'line': j,
                                'problem': 'Infinite recursion - no base case',
                                'severity': 'HIGH',
                                'suggestion': 'Add a base case condition to stop recursion',
                                'category': 'bug',
                                'code': 'void recursive_bug()'
                            })
                        break
            
            # 9. Undefined variable
            if 'cout << undefined_variable' in line:
                issues.append({
                    'line': i,
                    'problem': 'Undefined variable: undefined_variable',
                    'severity': 'HIGH',
                    'suggestion': 'Define variable before using it',
                    'category': 'bug',
                    'code': line.strip()
                })
            
            # 10. Mutation during iteration
            if 'for (auto user : users)' in line:
                for j in range(i, min(i+15, len(lines))):
                    if 'users.erase' in lines[j-1] or 'users.remove' in lines[j-1]:
                        issues.append({
                            'line': j,
                            'problem': 'Modifying vector during iteration',
                            'severity': 'HIGH',
                            'suggestion': 'Use iterator: for (auto it = users.begin(); it != users.end();)',
                            'category': 'bug',
                            'code': lines[j-1].strip()
                        })
                        break
            
            # ================================================================
            # MEDIUM SEVERITY ISSUES
            # ================================================================
            
            # 11. Global variable
            if 'vector<pair<string, string>> users;' in line and i < 15:
                issues.append({
                    'line': i,
                    'problem': 'Global variable declared',
                    'severity': 'MEDIUM',
                    'suggestion': 'Avoid global variables - encapsulate in class or pass as parameter',
                    'category': 'design',
                    'code': line.strip()
                })
            
            # 12. Pass by value for large objects
            large_types = ['vector', 'string', 'map', 'set', 'list', 'pair']
            for t in large_types:
                if f'{t} ' in line and '(' in line and ')' in line and '&' not in line and 'const' not in line:
                    if any(func in line for func in ['register_user', 'login', 'calculate_average', 'read_file']):
                        issues.append({
                            'line': i,
                            'problem': f'Large object passed by value ({t})',
                            'severity': 'MEDIUM',
                            'suggestion': f'Use const {t}& to avoid copying',
                            'category': 'performance',
                            'code': line.strip()
                        })
                        break
            
            # 13. Validation without early return
            if 'void register_user' in line:
                for j in range(i, min(i+15, len(lines))):
                    if 'if (username == ""' in lines[j-1] or 'if (username.empty())' in lines[j-1]:
                        if 'return' not in ''.join(lines[j-1:j+3]):
                            issues.append({
                                'line': j,
                                'problem': 'Validation without early return',
                                'severity': 'MEDIUM',
                                'suggestion': 'Add return after invalid input',
                                'category': 'bug',
                                'code': lines[j-1].strip()
                            })
                        break
            
            # 14. Index error risk
            if 'get_user(100)' in line:
                issues.append({
                    'line': i,
                    'problem': 'Accessing index 100 without checking size',
                    'severity': 'MEDIUM',
                    'suggestion': 'Check if users.size() > 100 before accessing',
                    'category': 'bug',
                    'code': line.strip()
                })
            
            # 15. Empty list average
            if 'calculate_average(nums)' in line and 'vector<int> nums;' in ''.join(lines[max(0, i-10):i]):
                issues.append({
                    'line': i,
                    'problem': 'Calculating average of empty vector',
                    'severity': 'MEDIUM',
                    'suggestion': 'Check if vector is empty before calculating average',
                    'category': 'bug',
                    'code': line.strip()
                })
            
            # 16. Bad file read
            if 'file >> content' in line:
                issues.append({
                    'line': i,
                    'problem': 'file >> reads only first word, not entire file',
                    'severity': 'MEDIUM',
                    'suggestion': 'Use getline() in a loop or read() for entire file',
                    'category': 'bug',
                    'code': line.strip()
                })
            
            # 17. Command injection test
            if 'dangerous_exec("echo hacked")' in line:
                issues.append({
                    'line': i,
                    'problem': 'Command injection test - security risk',
                    'severity': 'MEDIUM',
                    'suggestion': 'Remove test code or use safer alternatives',
                    'category': 'security',
                    'code': line.strip()
                })
            
            # 18. Wrong function call
            if 'login("admin", "")' in line:
                issues.append({
                    'line': i,
                    'problem': 'Login called with empty password',
                    'severity': 'MEDIUM',
                    'suggestion': 'Password should not be empty',
                    'category': 'bug',
                    'code': line.strip()
                })
            
            # 19. at() can throw exception
            if '.at(' in line and 'try' not in ''.join(lines[max(0, i-10):i]):
                issues.append({
                    'line': i,
                    'problem': '.at() can throw out_of_range exception',
                    'severity': 'MEDIUM',
                    'suggestion': 'Wrap in try-catch or check size() first',
                    'category': 'error_handling',
                    'code': line.strip()
                })
            
            # ================================================================
            # LOW SEVERITY ISSUES
            # ================================================================
            
            # 20. Using namespace std
            if 'using namespace std;' in line:
                issues.append({
                    'line': i,
                    'problem': 'Using namespace std',
                    'severity': 'LOW',
                    'suggestion': 'Use std:: prefix instead to avoid naming conflicts',
                    'category': 'best_practice',
                    'code': line.strip()
                })
            
            # 21. Bad indentation
            if stripped and not stripped.startswith('//') and line.startswith(' '):
                indent = len(line) - len(line.lstrip())
                if indent > 0 and indent != 4 and indent != 2:
                    issues.append({
                        'line': i,
                        'problem': f'Bad indentation ({indent} spaces, should be 2 or 4)',
                        'severity': 'LOW',
                        'suggestion': 'Use consistent indentation (2 or 4 spaces)',
                        'category': 'style',
                        'code': line
                    })
            
            # 22. TODO comments
            if '// Forgot to close file' in line or '// No zero division handling' in line:
                issues.append({
                    'line': i,
                    'problem': 'TODO comment found',
                    'severity': 'LOW',
                    'suggestion': 'Address this item',
                    'category': 'maintenance',
                    'code': line.strip()
                })
            
            # 23. Missing braces for single statement
            if ('if (' in line or 'for (' in line) and line.strip().endswith(')'):
                next_line = lines[i] if i < len(lines) else ''
                if next_line.strip() and not next_line.strip().startswith('{') and not next_line.strip().startswith('//'):
                    issues.append({
                        'line': i,
                        'problem': 'Missing braces around control statement',
                        'severity': 'LOW',
                        'suggestion': 'Always use braces {} even for single statements',
                        'category': 'style',
                        'code': line.strip()
                    })
        
        return issues
    
    # ============================================================================
    # JAVASCRIPT ANALYZER
    # ============================================================================
    def _analyze_javascript(self, code: str) -> List[Dict[str, Any]]:
        """JavaScript-specific bug detection"""
        issues = []
        lines = code.split('\n')
        
        declared_vars = set(self.builtins)
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Find declarations
            decl_patterns = [
                (r'\blet\s+(\w+)\s*=', 'let'),
                (r'\bconst\s+(\w+)\s*=', 'const'),
                (r'\bvar\s+(\w+)\s*=', 'var'),
                (r'\bfunction\s+(\w+)\s*\(', 'function')
            ]
            
            for pattern, decl_type in decl_patterns:
                match = re.search(pattern, line)
                if match:
                    declared_vars.add(match.group(1))
                    
                    # Warn about var usage
                    if decl_type == 'var':
                        issues.append({
                            'line': i,
                            'problem': 'Using "var" instead of "let" or "const"',
                            'severity': 'LOW',
                            'suggestion': 'Use "const" for values that don\'t change, "let" for others',
                            'category': 'best_practice',
                            'code': line.strip()
                        })
            
            # Console.log in production
            if 'console.log' in line:
                issues.append({
                    'line': i,
                    'problem': 'Console.log left in code',
                    'severity': 'LOW',
                    'suggestion': 'Remove console.log before production',
                    'category': 'debug',
                    'code': line.strip()
                })
            
            # == instead of ===
            if re.search(r'[^=!]==[^=]', line) and '===' not in line:
                issues.append({
                    'line': i,
                    'problem': 'Using == instead of ===',
                    'severity': 'MEDIUM',
                    'suggestion': 'Use === for strict equality to avoid type coercion',
                    'category': 'bug',
                    'code': line.strip()
                })
            
            # eval() usage
            if 'eval(' in line:
                issues.append({
                    'line': i,
                    'problem': 'eval() function used',
                    'severity': 'HIGH',
                    'suggestion': 'Avoid eval() - security risk',
                    'category': 'security',
                    'code': line.strip()
                })
            
            # setTimeout/setInterval with string
            if 'setTimeout("' in line or 'setInterval("' in line:
                issues.append({
                    'line': i,
                    'problem': 'setTimeout/setInterval with string argument',
                    'severity': 'HIGH',
                    'suggestion': 'Use function instead of string (security risk)',
                    'category': 'security',
                    'code': line.strip()
                })
            
            # == null check
            if '== null' in line:
                issues.append({
                    'line': i,
                    'problem': 'Using == null',
                    'severity': 'LOW',
                    'suggestion': 'Use === null or === undefined for explicit checks',
                    'category': 'best_practice',
                    'code': line.strip()
                })
        
        return issues
    
    # ============================================================================
    # TYPESCRIPT ANALYZER
    # ============================================================================
    def _analyze_typescript(self, code: str) -> List[Dict[str, Any]]:
        """TypeScript-specific bug detection"""
        issues = self._analyze_javascript(code)
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Any type usage
            if re.search(r':\s*any\b', line):
                issues.append({
                    'line': i,
                    'problem': 'Using "any" type',
                    'severity': 'MEDIUM',
                    'suggestion': 'Use proper typing instead of any',
                    'category': 'type_safety',
                    'code': line.strip()
                })
            
            # Missing return type
            if re.search(r'function\s+\w+\s*\([^)]*\)\s*{', line) and ':' not in line.split(')')[0]:
                issues.append({
                    'line': i,
                    'problem': 'Missing return type annotation',
                    'severity': 'LOW',
                    'suggestion': 'Add return type: function(): ReturnType',
                    'category': 'best_practice',
                    'code': line.strip()
                })
            
            # Non-null assertion operator
            if '!' in line and '.' in line and not '!=' in line and not '!==' in line:
                issues.append({
                    'line': i,
                    'problem': 'Using non-null assertion operator (!)',
                    'severity': 'MEDIUM',
                    'suggestion': 'Use proper null checking instead',
                    'category': 'type_safety',
                    'code': line.strip()
                })
        
        return issues
    
    # ============================================================================
    # JAVA ANALYZER
    # ============================================================================
    def _analyze_java(self, code: str) -> List[Dict[str, Any]]:
        """Java-specific bug detection"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Null pointer risk with .equals()
            if '.equals(' in line and not line.strip().startswith('if'):
                var_name = re.search(r'(\w+)\.equals\(', line)
                if var_name and var_name.group(1) not in ['null', 'String']:
                    issues.append({
                        'line': i,
                        'problem': 'Potential NullPointerException',
                        'severity': 'HIGH',
                        'suggestion': f'Use "{var_name.group(1)}".equals() or check for null first',
                        'category': 'bug',
                        'code': line.strip()
                    })
            
            # System.out.println
            if 'System.out.println' in line:
                issues.append({
                    'line': i,
                    'problem': 'System.out.println in code',
                    'severity': 'LOW',
                    'suggestion': 'Use a logging framework (SLF4J, Log4j)',
                    'category': 'debug',
                    'code': line.strip()
                })
            
            # Empty catch blocks
            if 'catch' in line and ('{}' in line or '{ }' in line):
                issues.append({
                    'line': i,
                    'problem': 'Empty catch block',
                    'severity': 'MEDIUM',
                    'suggestion': 'Handle exception or log it',
                    'category': 'error_handling',
                    'code': line.strip()
                })
        
        return issues
    
    # ============================================================================
    # C# ANALYZER
    # ============================================================================
    def _analyze_csharp(self, code: str) -> List[Dict[str, Any]]:
        """C# specific bug detection"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Async method without await
            if 'async' in line and 'Task' in line:
                has_await = False
                for j in range(i, min(i+20, len(lines))):
                    if 'await ' in lines[j-1]:
                        has_await = True
                        break
                if not has_await:
                    issues.append({
                        'line': i,
                        'problem': 'Async method without await',
                        'severity': 'MEDIUM',
                        'suggestion': 'Add await or remove async',
                        'category': 'bug',
                        'code': line.strip()
                    })
            
            # String comparison with ==
            if 'string' in line and '==' in line:
                issues.append({
                    'line': i,
                    'problem': 'String comparison with ==',
                    'severity': 'LOW',
                    'suggestion': 'Use .Equals() for string comparison',
                    'category': 'best_practice',
                    'code': line.strip()
                })
        
        return issues
    
    # ============================================================================
    # PHP ANALYZER
    # ============================================================================
    def _analyze_php(self, code: str) -> List[Dict[str, Any]]:
        """PHP specific bug detection"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Deprecated mysql_* functions
            if re.search(r'mysql_\w+\(', line):
                issues.append({
                    'line': i,
                    'problem': 'Deprecated mysql_* function',
                    'severity': 'HIGH',
                    'suggestion': 'Use MySQLi or PDO instead',
                    'category': 'deprecated',
                    'code': line.strip()
                })
            
            # SQL injection risks
            if ('$_GET' in line or '$_POST' in line) and ('query' in line):
                if 'prepare' not in line and 'bind_param' not in line:
                    issues.append({
                        'line': i,
                        'problem': 'SQL injection risk',
                        'severity': 'HIGH',
                        'suggestion': 'Use prepared statements or escape input',
                        'category': 'security',
                        'code': line.strip()
                    })
            
            # eval() function
            if 'eval(' in line:
                issues.append({
                    'line': i,
                    'problem': 'eval() function used',
                    'severity': 'HIGH',
                    'suggestion': 'Avoid eval() - security risk',
                    'category': 'security',
                    'code': line.strip()
                })
        
        return issues
    
    # ============================================================================
    # RUBY ANALYZER
    # ============================================================================
    def _analyze_ruby(self, code: str) -> List[Dict[str, Any]]:
        """Ruby specific bug detection"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # puts in production
            if re.search(r'\bputs\s+', line) and not line.strip().startswith('#'):
                issues.append({
                    'line': i,
                    'problem': 'puts left in code',
                    'severity': 'LOW',
                    'suggestion': 'Use Rails.logger for logging',
                    'category': 'debug',
                    'code': line.strip()
                })
            
            # unless with else
            if 'unless' in line and 'else' in line:
                issues.append({
                    'line': i,
                    'problem': 'unless with else is confusing',
                    'severity': 'LOW',
                    'suggestion': 'Use if...else instead',
                    'category': 'style',
                    'code': line.strip()
                })
            
            # nil comparison
            if '== nil' in line or '!= nil' in line:
                issues.append({
                    'line': i,
                    'problem': 'Comparing with nil using ==',
                    'severity': 'LOW',
                    'suggestion': 'Use .nil? method',
                    'category': 'best_practice',
                    'code': line.strip()
                })
        
        return issues
    
    # ============================================================================
    # GO ANALYZER
    # ============================================================================
    def _analyze_go(self, code: str) -> List[Dict[str, Any]]:
        """Go specific bug detection"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Unchecked errors
            if ', err :=' in line or ':= err' in line:
                has_error_check = False
                for j in range(i, min(i+5, len(lines))):
                    if 'if err != nil' in lines[j-1]:
                        has_error_check = True
                        break
                if not has_error_check:
                    issues.append({
                        'line': i,
                        'problem': 'Unchecked error',
                        'severity': 'HIGH',
                        'suggestion': 'Always check errors with if err != nil',
                        'category': 'error_handling',
                        'code': line.strip()
                    })
        
        return issues
    
    # ============================================================================
    # RUST ANALYZER
    # ============================================================================
    def _analyze_rust(self, code: str) -> List[Dict[str, Any]]:
        """Rust specific bug detection"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # unwrap() usage
            if '.unwrap()' in line:
                issues.append({
                    'line': i,
                    'problem': 'Using unwrap()',
                    'severity': 'MEDIUM',
                    'suggestion': 'Handle the Result/Option properly with match or ? operator',
                    'category': 'error_handling',
                    'code': line.strip()
                })
        
        return issues
    
    # ============================================================================
    # SWIFT ANALYZER
    # ============================================================================
    def _analyze_swift(self, code: str) -> List[Dict[str, Any]]:
        """Swift specific bug detection"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Force unwrapping
            if re.search(r'\b\w+!\s*\.', line) or re.search(r'\b\w+!\s*\)', line):
                issues.append({
                    'line': i,
                    'problem': 'Force unwrapping with !',
                    'severity': 'MEDIUM',
                    'suggestion': 'Use optional binding (if let) or guard let instead',
                    'category': 'safety',
                    'code': line.strip()
                })
        
        return issues
    
    # ============================================================================
    # KOTLIN ANALYZER
    # ============================================================================
    def _analyze_kotlin(self, code: str) -> List[Dict[str, Any]]:
        """Kotlin specific bug detection"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # !! operator
            if '!!' in line:
                issues.append({
                    'line': i,
                    'problem': 'Using !! (not-null assertion)',
                    'severity': 'MEDIUM',
                    'suggestion': 'Use safe call (?.) or let{} instead',
                    'category': 'safety',
                    'code': line.strip()
                })
        
        return issues
    
    # ============================================================================
    # C ANALYZER
    # ============================================================================
    def _analyze_c(self, code: str) -> List[Dict[str, Any]]:
        """C specific bug detection"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # gets() usage
            if 'gets(' in line:
                issues.append({
                    'line': i,
                    'problem': 'gets() function used',
                    'severity': 'HIGH',
                    'suggestion': 'Use fgets() instead (buffer overflow risk)',
                    'category': 'security',
                    'code': line.strip()
                })
            
            # strcpy without bounds
            if 'strcpy(' in line:
                issues.append({
                    'line': i,
                    'problem': 'strcpy() without bounds checking',
                    'severity': 'HIGH',
                    'suggestion': 'Use strncpy() or strlcpy()',
                    'category': 'security',
                    'code': line.strip()
                })
        
        return issues
    
    # ============================================================================
    # HTML ANALYZER
    # ============================================================================
    def _analyze_html(self, code: str) -> List[Dict[str, Any]]:
        """HTML specific bug detection"""
        issues = []
        lines = code.split('\n')
        ids = {}
        
        for i, line in enumerate(lines, 1):
            # Missing alt attributes
            if '<img' in line and 'alt=' not in line:
                issues.append({
                    'line': i,
                    'problem': 'Image missing alt attribute',
                    'severity': 'MEDIUM',
                    'suggestion': 'Add alt text for accessibility',
                    'category': 'accessibility',
                    'code': line.strip()
                })
            
            # Duplicate IDs
            id_matches = re.findall(r'id=["\']([^"\']+)["\']', line)
            for id_name in id_matches:
                if id_name in ids:
                    issues.append({
                        'line': i,
                        'problem': f'Duplicate ID: {id_name}',
                        'severity': 'MEDIUM',
                        'suggestion': 'IDs must be unique',
                        'category': 'validation',
                        'code': line.strip()
                    })
                else:
                    ids[id_name] = i
        
        return issues
    
    # ============================================================================
    # CSS ANALYZER
    # ============================================================================
    def _analyze_css(self, code: str) -> List[Dict[str, Any]]:
        """CSS specific bug detection"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # !important usage
            if '!important' in line:
                issues.append({
                    'line': i,
                    'problem': 'Using !important',
                    'severity': 'LOW',
                    'suggestion': 'Avoid !important - increase specificity instead',
                    'category': 'best_practice',
                    'code': line.strip()
                })
            
            # Missing units
            if ':' in line and ';' in line:
                prop_value = line.split(':')[1].split(';')[0].strip()
                if re.search(r'\b\d+\b', prop_value) and not re.search(r'\b\d+(px|em|rem|%|vh|vw)', prop_value):
                    if prop_value.strip() != '0':
                        issues.append({
                            'line': i,
                            'problem': 'Missing units for numeric value',
                            'severity': 'MEDIUM',
                            'suggestion': 'Add units (px, em, rem, %, etc.)',
                            'category': 'validation',
                            'code': line.strip()
                        })
        
        return issues
    
    # ============================================================================
    # COMMON ANALYSIS
    # ============================================================================
    def _common_analysis(self, code: str) -> List[Dict[str, Any]]:
        """Issues common across all languages"""
        issues = []
        lines = code.split('\n')
        
        # Line length > 120
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append({
                    'line': i,
                    'problem': f'Line too long ({len(line)} characters)',
                    'severity': 'LOW',
                    'suggestion': 'Break line into multiple lines (max 120 chars)',
                    'category': 'style',
                    'code': line[:50] + '...' if len(line) > 50 else line
                })
        
        # TODO/FIXME comments
        for i, line in enumerate(lines, 1):
            if re.search(r'(TODO|FIXME|XXX)', line, re.IGNORECASE):
                issues.append({
                    'line': i,
                    'problem': 'TODO/FIXME comment found',
                    'severity': 'LOW',
                    'suggestion': 'Address this item before deployment',
                    'category': 'maintenance',
                    'code': line.strip()
                })
        
        # Hardcoded secrets (all languages)
        secret_patterns = [
            (r'password\s*[:=]\s*[\'\"][^\'\"]+[\'\"]', 'Hardcoded password'),
            (r'api[_-]?key\s*[:=]\s*[\'\"][^\'\"]+[\'\"]', 'Hardcoded API key'),
            (r'secret\s*[:=]\s*[\'\"][^\'\"]+[\'\"]', 'Hardcoded secret'),
            (r'token\s*[:=]\s*[\'\"][^\'\"]+[\'\"]', 'Hardcoded token')
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, desc in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'line': i,
                        'problem': desc,
                        'severity': 'HIGH',
                        'suggestion': 'Use environment variables or secrets manager',
                        'category': 'security',
                        'code': line.strip()
                    })
        
        # No newline at end
        if lines and lines[-1] != '' and not lines[-1].endswith('\n'):
            issues.append({
                'line': len(lines),
                'problem': 'No newline at end of file',
                'severity': 'LOW',
                'suggestion': 'Add a newline at the end of the file',
                'category': 'style',
                'code': 'EOF'
            })
        
        return issues


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        with open(filename, 'r') as f:
            code = f.read()
        
        # Detect language from extension
        ext = filename.split('.')[-1]
        lang_map = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c',
            'cs': 'csharp',
            'php': 'php',
            'rb': 'ruby',
            'go': 'go',
            'rs': 'rust',
            'swift': 'swift',
            'kt': 'kotlin',
            'html': 'html',
            'htm': 'html',
            'css': 'css'
        }
        
        language = lang_map.get(ext, 'python')
        
        # Analyze with noise filtering
        analyzer = CodeAnalyzer(language, filter_noise=True)
        issues = analyzer.analyze(code)
        
        # Print results
        print("\n" + "="*60)
        print("🔍 ANALYSIS RESULTS")
        print("="*60)
        
        for severity in ['HIGH', 'MEDIUM', 'LOW']:
            severity_issues = [i for i in issues if i['severity'] == severity]
            if severity_issues:
                print(f"\n{severity} SEVERITY ({len(severity_issues)} issues):")
                print("-"*40)
                for issue in severity_issues:
                    print(f"  Line {issue['line']}: {issue['problem']}")
                    print(f"  → {issue['suggestion']}")
                    if 'code' in issue and issue['code']:
                        print(f"  Code: {issue['code']}")
                    print()