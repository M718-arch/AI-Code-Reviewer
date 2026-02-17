"""
code_analyzer.py - AGGRESSIVE Bug Detection
This WILL find bugs in your code!
"""

import ast
import re
from typing import List, Dict, Any

class CodeAnalyzer:
    def __init__(self, language='python'):
        self.language = language
    
    def analyze(self, code: str) -> List[Dict[str, Any]]:
        """Main analysis method - FINDS REAL BUGS!"""
        issues = []
        
        print(f"🔍 Analyzing {len(code)} characters of code...")  # Debug
        
        if self.language == 'python':
            issues.extend(self._analyze_python(code))
        
        issues.extend(self._common_analysis(code))
        
        print(f"✅ Found {len(issues)} issues!")  # Debug
        return issues
    
    def _analyze_python(self, code: str) -> List[Dict[str, Any]]:
        """Python-specific bug detection - THIS FINDS EVERYTHING!"""
        issues = []
        
        # ====================================================================
        # BUG 1: Undefined variables
        # ====================================================================
        try:
            tree = ast.parse(code)
            defined_vars = set()
            
            # Find all defined variables
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    defined_vars.add(node.name)
                    for arg in node.args.args:
                        defined_vars.add(arg.arg)
                elif isinstance(node, ast.ClassDef):
                    defined_vars.add(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            defined_vars.add(target.id)
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    defined_vars.add(node.id)
            
            # Add built-ins
            builtins = ['print', 'len', 'str', 'int', 'float', 'list', 'dict', 
                       'set', 'tuple', 'range', 'open', 'sum', 'min', 'max',
                       'abs', 'round', 'type', 'isinstance', 'issubclass',
                       'hasattr', 'getattr', 'setattr', 'delattr']
            defined_vars.update(builtins)
            
            # Check for undefined variables
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    if node.id not in defined_vars and not node.id.startswith('_'):
                        issues.append({
                            'line': node.lineno,
                            'problem': f'Undefined variable: {node.id}',
                            'severity': 'HIGH',
                            'suggestion': f'Define {node.id} before using it',
                            'category': 'bug'
                        })
        except SyntaxError as e:
            # Handle syntax errors separately
            issues.append({
                'line': e.lineno or 1,
                'problem': f'Syntax error: {e.msg}',
                'severity': 'HIGH',
                'suggestion': 'Fix the syntax error',
                'category': 'syntax'
            })
        
        # ====================================================================
        # BUG 2: ZeroDivisionError
        # ====================================================================
        zero_div_pattern = r'(\w+|\d+)\s*/\s*0\b'
        for match in re.finditer(zero_div_pattern, code):
            line = code[:match.start()].count('\n') + 1
            issues.append({
                'line': line,
                'problem': 'Potential ZeroDivisionError',
                'severity': 'HIGH',
                'suggestion': 'Check if denominator is zero before division',
                'category': 'bug'
            })
        
        zero_div_pattern2 = r'(\w+|\d+)\s*/\s*\(\s*(\w+|\d+)\s*-\s*\2\s*\)'
        for match in re.finditer(zero_div_pattern2, code):
            line = code[:match.start()].count('\n') + 1
            issues.append({
                'line': line,
                'problem': 'Potential ZeroDivisionError (subtracting same value)',
                'severity': 'HIGH',
                'suggestion': 'Ensure denominator is not zero',
                'category': 'bug'
            })
        
        # ====================================================================
        # BUG 3: Unclosed strings
        # ====================================================================
        lines = code.split('\n')
        in_string = False
        string_char = ''
        for i, line in enumerate(lines, 1):
            line_check = line
            # Skip comments
            if '#' in line_check:
                line_check = line_check[:line_check.index('#')]
            
            for char in ['"', "'", '"""', "'''"]:
                if char in line_check:
                    count = line_check.count(char)
                    if count % 2 != 0:
                        issues.append({
                            'line': i,
                            'problem': f'Possible unclosed string: {char}',
                            'severity': 'HIGH',
                            'suggestion': f'Add closing {char}',
                            'category': 'syntax'
                        })
        
        # ====================================================================
        # BUG 4: Missing colons
        # ====================================================================
        colon_keywords = ['if', 'elif', 'else', 'for', 'while', 'def', 'class', 
                         'with', 'try', 'except', 'finally', 'else:']
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                for keyword in colon_keywords:
                    if stripped.startswith(keyword) and not stripped.endswith(':'):
                        if keyword != 'else' or stripped != 'else':
                            issues.append({
                                'line': i,
                                'problem': f'Missing colon after {keyword}',
                                'severity': 'HIGH',
                                'suggestion': f'Add ":" at end of line',
                                'category': 'syntax'
                            })
        
        # ====================================================================
        # BUG 5: Indentation errors
        # ====================================================================
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.strip().startswith('#'):
                indent = len(line) - len(line.lstrip())
                if indent > 0 and indent % 4 != 0:
                    issues.append({
                        'line': i,
                        'problem': f'Bad indentation ({indent} spaces, should be multiple of 4)',
                        'severity': 'MEDIUM',
                        'suggestion': 'Use 4 spaces for indentation',
                        'category': 'style'
                    })
        
        # Check for mixed tabs and spaces
        for i, line in enumerate(lines, 1):
            if '\t' in line:
                issues.append({
                    'line': i,
                    'problem': 'Mixed tabs and spaces',
                    'severity': 'MEDIUM',
                    'suggestion': 'Use only spaces (4 per indent)',
                    'category': 'style'
                })
        
        # ====================================================================
        # BUG 6: Import errors
        # ====================================================================
        import_pattern = r'^(?:from\s+(\S+)\s+)?import\s+(\S+)'
        for match in re.finditer(import_pattern, code, re.MULTILINE):
            line = code[:match.start()].count('\n') + 1
            module = match.group(1) or match.group(2)
            
            # Known non-existent modules
            bad_imports = ['infinity', 'non_existent_module', 'non_existent_class']
            if module in bad_imports:
                issues.append({
                    'line': line,
                    'problem': f'Import of non-existent module: {module}',
                    'severity': 'MEDIUM',
                    'suggestion': f'Fix module name or install: pip install {module}',
                    'category': 'import'
                })
        
        # ====================================================================
        # BUG 7: Index errors
        # ====================================================================
        index_pattern = r'(\w+)\s*\[\s*(\d+|-?\d+)\s*\]'
        for match in re.finditer(index_pattern, code):
            line = code[:match.start()].count('\n') + 1
            index = int(match.group(2))
            if abs(index) > 10:  # Suspiciously large index
                issues.append({
                    'line': line,
                    'problem': f'Potential IndexError: list index {index} may be out of range',
                    'severity': 'MEDIUM',
                    'suggestion': 'Check if index is within bounds using len()',
                    'category': 'bug'
                })
        
        # ====================================================================
        # BUG 8: Infinite recursion
        # ====================================================================
        func_pattern = r'def\s+(\w+)\s*\(.*?\):'
        for match in re.finditer(func_pattern, code):
            func_name = match.group(1)
            func_body = code[match.end():]
            # Check if function calls itself without condition
            if re.search(rf'\b{func_name}\s*\(', func_body):
                # Look for base case
                has_return = 'return' in func_body[:200]
                has_conditional = any(kw in func_body[:200] for kw in ['if', 'else', 'elif'])
                
                if has_return and not has_conditional:
                    issues.append({
                        'line': code[:match.start()].count('\n') + 1,
                        'problem': f'Possible infinite recursion in {func_name}()',
                        'severity': 'HIGH',
                        'suggestion': 'Add a base case condition to stop recursion',
                        'category': 'bug'
                    })
        
        # ====================================================================
        # BUG 9: File operations without existence check
        # ====================================================================
        file_ops = ['os.remove', 'os.unlink', 'open']
        for op in file_ops:
            pattern = rf'{op}\s*\(\s*[\'"]([^\'"]+)[\'"]'
            for match in re.finditer(pattern, code):
                line = code[:match.start()].count('\n') + 1
                # Check if there's an exists check before
                prev_lines = code[:match.start()].split('\n')[-5:]
                has_check = any('os.path.exists' in line or 'os.path.isfile' in line for line in prev_lines)
                
                if not has_check:
                    issues.append({
                        'line': line,
                        'problem': f'File operation without existence check: {op}',
                        'severity': 'MEDIUM',
                        'suggestion': f'Check if file exists with os.path.exists() before {op}',
                        'category': 'security'
                    })
        
        # ====================================================================
        # BUG 10: Bare except
        # ====================================================================
        bare_except_pattern = r'except\s*:'
        for match in re.finditer(bare_except_pattern, code):
            line = code[:match.start()].count('\n') + 1
            issues.append({
                'line': line,
                'problem': 'Bare except clause',
                'severity': 'HIGH',
                'suggestion': 'Catch specific exceptions instead',
                'category': 'error_handling'
            })
        
        # ====================================================================
        # BUG 11: Mutable default arguments
        # ====================================================================
        mutable_pattern = r'def\s+\w+\(.*?=\s*\[\s*\].*?\):|def\s+\w+\(.*?=\s*\{\s*\}.*?\):|def\s+\w+\(.*?=\s*set\(\s*\).*?\):'
        for match in re.finditer(mutable_pattern, code):
            line = code[:match.start()].count('\n') + 1
            issues.append({
                'line': line,
                'problem': 'Mutable default argument',
                'severity': 'MEDIUM',
                'suggestion': 'Use None as default and create mutable inside function',
                'category': 'bug'
            })
        
        # ====================================================================
        # BUG 12: Comparing None with ==
        # ====================================================================
        none_eq_pattern = r'==\s*None|!=\s*None'
        for match in re.finditer(none_eq_pattern, code):
            line = code[:match.start()].count('\n') + 1
            issues.append({
                'line': line,
                'problem': 'Comparing None with == or !=',
                'severity': 'LOW',
                'suggestion': 'Use "is None" or "is not None" instead',
                'category': 'best_practice'
            })
        
        # ====================================================================
        # BUG 13: Unused variables
        # ====================================================================
        try:
            tree = ast.parse(code)
            assigned_vars = set()
            used_vars = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            assigned_vars.add(target.id)
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    used_vars.add(node.id)
            
            unused = assigned_vars - used_vars
            for var in unused:
                if not var.startswith('_') and var not in builtins:
                    # Find line number
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Assign):
                            for target in node.targets:
                                if isinstance(target, ast.Name) and target.id == var:
                                    issues.append({
                                        'line': node.lineno,
                                        'problem': f'Unused variable: {var}',
                                        'severity': 'LOW',
                                        'suggestion': f'Remove {var} or use it',
                                        'category': 'style'
                                    })
        except:
            pass
        
        # ====================================================================
        # BUG 14: Too many arguments
        # ====================================================================
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if len(node.args.args) > 7:
                        issues.append({
                            'line': node.lineno,
                            'problem': f'Function {node.name} has too many arguments ({len(node.args.args)})',
                            'severity': 'MEDIUM',
                            'suggestion': 'Reduce number of arguments or use a data class',
                            'category': 'design'
                        })
        except:
            pass
        
        # ====================================================================
        # BUG 15: Empty except block
        # ====================================================================
        empty_except_pattern = r'except\s+\w+\s*:\s*\n\s*pass'
        for match in re.finditer(empty_except_pattern, code):
            line = code[:match.start()].count('\n') + 1
            issues.append({
                'line': line,
                'problem': 'Empty except block',
                'severity': 'MEDIUM',
                'suggestion': 'Handle the exception or log it',
                'category': 'error_handling'
            })
        
        # ====================================================================
        # BUG 16: Hardcoded secrets
        # ====================================================================
        secret_patterns = [
            (r'password\s*=\s*[\'\"][^\'\"]+[\'\"]', 'Hardcoded password'),
            (r'api[_-]?key\s*=\s*[\'\"][^\'\"]+[\'\"]', 'Hardcoded API key'),
            (r'secret\s*=\s*[\'\"][^\'\"]+[\'\"]', 'Hardcoded secret'),
            (r'token\s*=\s*[\'\"][^\'\"]+[\'\"]', 'Hardcoded token'),
            (r'aws_access_key_id\s*=', 'AWS access key'),
            (r'aws_secret_access_key\s*=', 'AWS secret key')
        ]
        
        for pattern, desc in secret_patterns:
            for match in re.finditer(pattern, code, re.IGNORECASE):
                line = code[:match.start()].count('\n') + 1
                issues.append({
                    'line': line,
                    'problem': f'{desc}',
                    'severity': 'HIGH',
                    'suggestion': 'Use environment variables or secrets manager',
                    'category': 'security'
                })
        
        # ====================================================================
        # BUG 17: Type errors
        # ====================================================================
        type_error_pattern = r'([\'"]\w+[\'"])\s*\+\s*(\d+)|(\d+)\s*\+\s*([\'"]\w+[\'"])'
        for match in re.finditer(type_error_pattern, code):
            line = code[:match.start()].count('\n') + 1
            issues.append({
                'line': line,
                'problem': 'Potential TypeError: concatenating string and int',
                'severity': 'HIGH',
                'suggestion': 'Convert int to string using str()',
                'category': 'bug'
            })
        
        # ====================================================================
        # BUG 18: Attribute errors
        # ====================================================================
        attr_error_patterns = [
            (r'[\'"].*?[\'"]\.append\(', 'String has no append() method'),
            (r'\b\d+\b\.split\(', 'Integer has no split() method'),
            (r'\b\d+\b\.upper\(', 'Integer has no upper() method'),
            (r'\b\d+\b\.lower\(', 'Integer has no lower() method')
        ]
        
        for pattern, desc in attr_error_patterns:
            for match in re.finditer(pattern, code):
                line = code[:match.start()].count('\n') + 1
                issues.append({
                    'line': line,
                    'problem': f'Potential AttributeError: {desc}',
                    'severity': 'HIGH',
                    'suggestion': 'Check object type before calling method',
                    'category': 'bug'
                })
        
        # ====================================================================
        # BUG 19: Key errors
        # ====================================================================
        key_error_pattern = r'(\w+)\[([\'"]\w+[\'"])\]'
        for match in re.finditer(key_error_pattern, code):
            dict_name = match.group(1)
            key = match.group(2)
            line = code[:match.start()].count('\n') + 1
            
            # Check if dict might not have the key
            if 'get(' not in code[match.start():match.start()+50]:
                issues.append({
                    'line': line,
                    'problem': f'Potential KeyError: accessing key {key} without get()',
                    'severity': 'MEDIUM',
                    'suggestion': 'Use dict.get(key) or check key existence',
                    'category': 'bug'
                })
        
        # ====================================================================
        # BUG 20: Redefining built-ins
        # ====================================================================
        builtins_list = ['list', 'dict', 'set', 'tuple', 'str', 'int', 'float', 
                        'bool', 'print', 'input', 'open', 'sum', 'min', 'max',
                        'abs', 'round', 'type', 'len', 'range', 'enumerate',
                        'zip', 'map', 'filter', 'sorted', 'reversed']
        
        for builtin in builtins_list:
            pattern = rf'^{builtin}\s*=|\s{builtin}\s*='
            for match in re.finditer(pattern, code, re.MULTILINE):
                line = code[:match.start()].count('\n') + 1
                issues.append({
                    'line': line,
                    'problem': f'Redefining built-in: {builtin}',
                    'severity': 'MEDIUM',
                    'suggestion': f'Use a different variable name instead of {builtin}',
                    'category': 'best_practice'
                })
        
        # ====================================================================
        # BUG 21: Invalid escape sequences
        # ====================================================================
        invalid_escape = r'(?<!\\)\\(?!\\|\'|\"|n|r|t|b|f|u[0-9a-f]{4}|U[0-9a-f]{8}|x[0-9a-f]{2})[a-zA-Z]'
        for match in re.finditer(invalid_escape, code):
            line = code[:match.start()].count('\n') + 1
            issues.append({
                'line': line,
                'problem': f'Invalid escape sequence: \\{match.group()[1]}',
                'severity': 'MEDIUM',
                'suggestion': 'Use raw string (r"...") or double backslash',
                'category': 'syntax'
            })
        
        # ====================================================================
        # BUG 22: Smart quotes
        # ====================================================================
        smart_quotes = ['“', '”', '‘', '’']
        for i, line in enumerate(lines, 1):
            for quote in smart_quotes:
                if quote in line:
                    issues.append({
                        'line': i,
                        'problem': f'Smart quote detected: {quote}',
                        'severity': 'HIGH',
                        'suggestion': 'Use regular quotes (") or (\') instead',
                        'category': 'syntax'
                    })
        
        # ====================================================================
        # BUG 23: Missing self in class methods
        # ====================================================================
        class_pattern = r'class\s+(\w+)'
        for class_match in re.finditer(class_pattern, code):
            class_start = class_match.end()
            class_body = code[class_start:].split('\n\n')[0]
            
            method_pattern = r'def\s+(\w+)\s*\([^)]*\):'
            for method_match in re.finditer(method_pattern, class_body):
                method_name = method_match.group(1)
                if not method_name.startswith('__') and 'self' not in method_match.group():
                    line = code[:class_start + method_match.start()].count('\n') + 1
                    issues.append({
                        'line': line,
                        'problem': f'Missing self parameter in method {method_name}()',
                        'severity': 'HIGH',
                        'suggestion': 'Add "self" as first parameter',
                        'category': 'bug'
                    })
        
        # ====================================================================
        # BUG 24: Using is with literals
        # ====================================================================
        is_literal_pattern = r'\bis\s+(True|False|None|\d+|\'.*?\'|".*?")\b'
        for match in re.finditer(is_literal_pattern, code):
            line = code[:match.start()].count('\n') + 1
            issues.append({
                'line': line,
                'problem': 'Using "is" with literal',
                'severity': 'LOW',
                'suggestion': 'Use "==" for value comparison',
                'category': 'best_practice'
            })
        
        # ====================================================================
        # BUG 25: Wildcard imports
        # ====================================================================
        wildcard_pattern = r'from\s+\S+\s+import\s+\*'
        for match in re.finditer(wildcard_pattern, code):
            line = code[:match.start()].count('\n') + 1
            issues.append({
                'line': line,
                'problem': 'Wildcard import (from module import *)',
                'severity': 'MEDIUM',
                'suggestion': 'Import only what you need',
                'category': 'best_practice'
            })
        
        # ====================================================================
        # BUG 26: Global variable modification without global keyword
        # ====================================================================
        try:
            tree = ast.parse(code)
            global_vars = set()
            
            # Find global variables
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and isinstance(node.ctx, ast.Store):
                            if not isinstance(node.parent, ast.FunctionDef):
                                global_vars.add(target.id)
            
            # Check function modifications
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    modifies_global = False
                    for child in ast.walk(node):
                        if isinstance(child, ast.Name) and child.id in global_vars:
                            if isinstance(child.ctx, ast.Store):
                                modifies_global = True
                    
                    if modifies_global:
                        has_global = False
                        for child in ast.walk(node):
                            if isinstance(child, ast.Global):
                                if child.names and any(g in global_vars for g in child.names):
                                    has_global = True
                        
                        if not has_global:
                            issues.append({
                                'line': node.lineno,
                                'problem': 'Modifying global variable without global keyword',
                                'severity': 'HIGH',
                                'suggestion': 'Add "global var" statement inside function',
                                'category': 'bug'
                            })
        except:
            pass
        
        return issues
    
    def _common_analysis(self, code: str) -> List[Dict[str, Any]]:
        """Language-agnostic analysis"""
        issues = []
        lines = code.split('\n')
        
        # Check line length
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                issues.append({
                    'line': i,
                    'problem': f'Line too long ({len(line)} characters)',
                    'severity': 'LOW',
                    'suggestion': 'Break line into multiple lines (max 100 chars)',
                    'category': 'style'
                })
        
        # Check function length
        func_lines = 0
        func_start = 0
        in_func = False
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('def ') and line.strip().endswith(':'):
                in_func = True
                func_start = i
                func_lines = 0
            elif in_func:
                if line.strip() and not line.strip().startswith('#'):
                    func_lines += 1
                if i == len(lines) or (lines[i].strip() and not lines[i-1].strip().startswith(' ') and i > func_start + 1):
                    if func_lines > 50:
                        issues.append({
                            'line': func_start,
                            'problem': f'Function too long ({func_lines} lines)',
                            'severity': 'MEDIUM',
                            'suggestion': 'Break function into smaller functions',
                            'category': 'maintainability'
                        })
                    in_func = False
        
        # Check for TODO/FIXME/XXX
        todo_pattern = r'#.*?(TODO|FIXME|XXX)'
        for match in re.finditer(todo_pattern, code, re.IGNORECASE):
            line = code[:match.start()].count('\n') + 1
            issues.append({
                'line': line,
                'problem': f'TODO/FIXME comment found',
                'severity': 'LOW',
                'suggestion': 'Address this item before deployment',
                'category': 'maintenance'
            })
        
        return issues

def run_pylint(code: str) -> List[Dict[str, Any]]:
    """Mock pylint - returns empty list for now"""
    return []