"""
code_analyzer.py - Balanced Python Code Analyzer
Finds real issues with minimal false positives
"""

import ast
import re
import builtins
from typing import List, Dict, Any, Set, Optional
from pathlib import Path

class CodeAnalyzer:
    def __init__(self, language='python'):
        self.language = language
        self.builtins = set(dir(builtins))
        
    def analyze(self, code: str) -> List[Dict[str, Any]]:
        """Main analysis method - finds REAL issues"""
        issues = []
        
        if self.language == 'python':
            issues.extend(self._analyze_python(code))
        
        issues.extend(self._common_analysis(code))
        
        # Sort by severity: HIGH > MEDIUM > LOW
        severity_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        issues.sort(key=lambda x: severity_order.get(x['severity'], 3))
        
        return issues
    
    def _analyze_python(self, code: str) -> List[Dict[str, Any]]:
        """Python-specific analysis using AST where possible"""
        issues = []
        
        try:
            tree = ast.parse(code)
            
            # Track defined names with scope
            analyzer = ScopeAnalyzer()
            analyzer.visit(tree)
            
            # ====================================================================
            # 1. SYNTAX ERRORS - Already caught by ast.parse
            # ====================================================================
            
            # ====================================================================
            # 2. MUTABLE DEFAULT ARGUMENTS
            # ====================================================================
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for default in node.args.defaults:
                        if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                            issues.append({
                                'line': node.lineno,
                                'problem': f'Mutable default argument in {node.name}()',
                                'severity': 'HIGH',
                                'suggestion': 'Use None as default and create mutable inside function',
                                'category': 'bug',
                                'code': f'def {node.name}(...)'
                            })
            
            # ====================================================================
            # 3. BARE EXCEPT CLAUSES
            # ====================================================================
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        issues.append({
                            'line': node.lineno,
                            'problem': 'Bare except clause',
                            'severity': 'HIGH',
                            'suggestion': 'Catch specific exceptions (except ValueError:)',
                            'category': 'error_handling',
                            'code': 'except:'
                        })
            
            # ====================================================================
            # 4. HARDCODED SECRETS
            # ====================================================================
            secret_patterns = [
                (r'password\s*=\s*[\'\"][^\'\"]{8,}[\'\"]', 'Hardcoded password'),
                (r'(api[_-]?key|apikey)\s*=\s*[\'\"][^\'\"]+[\'\"]', 'Hardcoded API key'),
                (r'secret\s*=\s*[\'\"][^\'\"]+[\'\"]', 'Hardcoded secret'),
                (r'token\s*=\s*[\'\"][^\'\"]+[\'\"]', 'Hardcoded token'),
            ]
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant):
                            var_name = target.id.lower()
                            if any(secret in var_name for secret in ['password', 'api', 'secret', 'token']):
                                if isinstance(node.value.value, str) and len(node.value.value) > 8:
                                    issues.append({
                                        'line': node.lineno,
                                        'problem': f'Possible hardcoded {var_name}',
                                        'severity': 'HIGH',
                                        'suggestion': 'Use environment variables or a secrets manager',
                                        'category': 'security',
                                        'code': f'{target.id} = "********"'
                                    })
            
            # ====================================================================
            # 5. REDEFINING BUILT-INS
            # ====================================================================
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name in self.builtins:
                    issues.append({
                        'line': node.lineno,
                        'problem': f'Function redefines built-in: {node.name}()',
                        'severity': 'MEDIUM',
                        'suggestion': f'Rename function (built-in {node.name} already exists)',
                        'category': 'best_practice',
                        'code': f'def {node.name}('
                    })
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    if node.id in self.builtins and node.id not in ['__file__', '__name__']:
                        issues.append({
                            'line': node.lineno,
                            'problem': f'Variable redefines built-in: {node.id}',
                            'severity': 'MEDIUM',
                            'suggestion': f'Use a different variable name',
                            'category': 'best_practice',
                            'code': f'{node.id} = ...'
                        })
            
            # ====================================================================
            # 6. MISSING SELF IN CLASS METHODS
            # ====================================================================
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # Skip staticmethod and classmethod
                            has_decorator = any(
                                isinstance(d, ast.Name) and d.id in ['staticmethod', 'classmethod']
                                for d in item.decorator_list
                            )
                            
                            if not has_decorator and not item.name.startswith('__'):
                                if not item.args.args or item.args.args[0].arg != 'self':
                                    issues.append({
                                        'line': item.lineno,
                                        'problem': f'Method {item.name}() missing self parameter',
                                        'severity': 'HIGH',
                                        'suggestion': 'Add "self" as first parameter',
                                        'category': 'bug',
                                        'code': f'def {item.name}(self, ...)'
                                    })
            
            # ====================================================================
            # 7. COMPARING WITH NONE USING ==
            # ====================================================================
            for node in ast.walk(tree):
                if isinstance(node, ast.Compare):
                    for op in node.ops:
                        if isinstance(op, (ast.Eq, ast.NotEq)):
                            for comparator in node.comparators:
                                if isinstance(comparator, ast.Constant) and comparator.value is None:
                                    issues.append({
                                        'line': node.lineno,
                                        'problem': 'Comparing None with == or !=',
                                        'severity': 'LOW',
                                        'suggestion': 'Use "is None" or "is not None"',
                                        'category': 'best_practice',
                                        'code': 'x == None'
                                    })
            
            # ====================================================================
            # 8. WILDCARD IMPORTS
            # ====================================================================
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and node.names[0].name == '*':
                        issues.append({
                            'line': node.lineno,
                            'problem': f'Wildcard import: from {node.module} import *',
                            'severity': 'MEDIUM',
                            'suggestion': 'Import only what you need',
                            'category': 'best_practice',
                            'code': f'from {node.module} import *'
                        })
            
            # ====================================================================
            # 9. EMPTY EXCEPT BLOCK
            # ====================================================================
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
            
            # ====================================================================
            # 10. TOO MANY ARGUMENTS
            # ====================================================================
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    arg_count = len(node.args.args)
                    if arg_count > 7:
                        issues.append({
                            'line': node.lineno,
                            'problem': f'Function {node.name}() has {arg_count} arguments',
                            'severity': 'MEDIUM',
                            'suggestion': 'Consider using a dataclass or reducing arguments',
                            'category': 'design',
                            'code': f'def {node.name}({", ".join(a.arg for a in node.args.args[:3])}...)'
                        })
            
            # ====================================================================
            # 11. VERY LONG FUNCTIONS
            # ====================================================================
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Count non-empty, non-decorator lines
                    line_count = node.end_lineno - node.lineno + 1 if node.end_lineno else 0
                    if line_count > 80:
                        issues.append({
                            'line': node.lineno,
                            'problem': f'Function {node.name}() is very long ({line_count} lines)',
                            'severity': 'MEDIUM',
                            'suggestion': 'Break into smaller functions',
                            'category': 'maintainability',
                            'code': f'def {node.name}(): ...'
                        })
            
            # ====================================================================
            # 12. USING IS WITH LITERALS
            # ====================================================================
            for node in ast.walk(tree):
                if isinstance(node, ast.Compare):
                    for op in node.ops:
                        if isinstance(op, ast.Is):
                            for comparator in node.comparators:
                                if isinstance(comparator, ast.Constant) and comparator.value in [True, False, None]:
                                    pass  # This is actually correct
                                elif isinstance(comparator, (ast.Constant, ast.Num, ast.Str)):
                                    issues.append({
                                        'line': node.lineno,
                                        'problem': 'Using "is" with literal',
                                        'severity': 'LOW',
                                        'suggestion': 'Use "==" for value comparison',
                                        'category': 'best_practice',
                                        'code': 'x is 5'
                                    })
            
        except SyntaxError as e:
            issues.append({
                'line': e.lineno or 1,
                'problem': f'Syntax error: {e.msg}',
                'severity': 'HIGH',
                'suggestion': 'Fix the syntax error',
                'category': 'syntax',
                'code': code.split('\n')[e.lineno - 1] if e.lineno else ''
            })
        except Exception as e:
            # Log but don't crash
            print(f"Analysis error: {e}")
        
        return issues
    
    def _common_analysis(self, code: str) -> List[Dict[str, Any]]:
        """Language-agnostic analysis (minimal, low-noise checks)"""
        issues = []
        lines = code.split('\n')
        
        # Check line length (only obvious cases)
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append({
                    'line': i,
                    'problem': f'Line too long ({len(line)} chars)',
                    'severity': 'LOW',
                    'suggestion': 'Break line into multiple lines',
                    'category': 'style',
                    'code': line[:50] + '...'
                })
        
        # Check for TODO/FIXME comments
        for i, line in enumerate(lines, 1):
            if '#' in line:
                comment = line[line.index('#'):].lower()
                if 'todo' in comment or 'fixme' in comment or 'xxx' in comment:
                    issues.append({
                        'line': i,
                        'problem': 'TODO/FIXME comment found',
                        'severity': 'LOW',
                        'suggestion': 'Address before deployment',
                        'category': 'maintenance',
                        'code': line.strip()
                    })
        
        return issues


class ScopeAnalyzer(ast.NodeVisitor):
    """Tracks variable scope for accurate undefined variable detection"""
    
    def __init__(self):
        self.scopes = [set()]  # Stack of scopes
        self.imported_names = set()
        self.builtins = set(dir(builtins))
        
    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname or alias.name
            self.scopes[-1].add(name)
            self.imported_names.add(name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.name != '*':
                name = alias.asname or alias.name
                self.scopes[-1].add(name)
                self.imported_names.add(name)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        # New scope
        self.scopes.append(set())
        # Add function name to outer scope
        self.scopes[-2].add(node.name)
        # Add arguments
        for arg in node.args.args:
            self.scopes[-1].add(arg.arg)
        if node.args.vararg:
            self.scopes[-1].add(node.args.vararg.arg)
        if node.args.kwarg:
            self.scopes[-1].add(node.args.kwarg.arg)
        
        self.generic_visit(node)
        self.scopes.pop()
    
    def visit_ClassDef(self, node):
        self.scopes[-1].add(node.name)
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        for target in node.targets:
            self._add_target(target)
        self.generic_visit(node)
    
    def visit_AnnAssign(self, node):
        if node.target:
            self._add_target(node.target)
        self.generic_visit(node)
    
    def visit_For(self, node):
        self._add_target(node.target)
        self.generic_visit(node)
    
    def visit_With(self, node):
        for item in node.items:
            if item.optional_vars:
                self._add_target(item.optional_vars)
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        if node.name:
            self.scopes[-1].add(node.name)
        self.generic_visit(node)
    
    def _add_target(self, target):
        if isinstance(target, ast.Name):
            self.scopes[-1].add(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                self._add_target(elt)


# For testing
if __name__ == "__main__":
    analyzer = CodeAnalyzer()
    
    test_code = """
import os
from pathlib import Path

def bad_function(password="secret123"):
    x = []
    try:
        result = 10 / 0
    except:
        pass
    
    if result == None:
        print("Got none")
    
    return x

class Test:
    def missing_self():
        pass
"""
    
    issues = analyzer.analyze(test_code)
    for issue in issues:
        print(f"[{issue['severity']}] Line {issue['line']}: {issue['problem']}")
        print(f"    Suggestion: {issue['suggestion']}")
        if 'code' in issue:
            print(f"    Code: {issue['code']}")
        print()