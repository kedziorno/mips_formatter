import re
from typing import List, Tuple, Dict
from collections import defaultdict

# PicoBlaze instruction set obtained from 
# https://www1.hs-bremerhaven.de/kmueller/VHDL/Instr_summ_PicoBlaze.pdf
instructions = '|'.join([
    'load', 
    'jump',
    'rl',                 'll',
    'call',               'return',
    'compare',            'test',
    'fetch',              'store',
    'input',              'output',
    'disable interrupt',  'enable interrupt',
    'returni disable',    'returni enable',
    'and',                'or',               'xor',
    'add',                'addcy',            'sub',  'subcy',
    'sl0',                'sla',              'slx',  'sl1',
    'sr0',                'sra',              'srx',  'sr1'
])
directives = '|'.join([
    'constant', 'namereg'
])
registers = '|'.join([
'[st][0-9a-fA-F]', 'A'
])
specs_string = [
'LABEL_DEFINITION', # 0
'DIRECTIVE',        # 1
'INSTRUCTION',      # 2
'REGISTER',         # 3
'COMMA',            # 4
'INTEGER',          # 5
'CHAR',             # 6
'COMMENT',          # 7
'STRING',           # 8
'FLOAT',            # 9
'LBRACKET',         # 10
'RBRACKET',         # 11
'WHITESPACE',       # 12
'UNKNOWN'           # 13
]

token_specs = {}
token_specs[specs_string[0]] = (specs_string[0], r'([a-zA-Z0-9_ ]+:)[\s]{0,}\s*');
token_specs[specs_string[1]] = (specs_string[1], fr'[\s]*(?:{directives})\b');
token_specs[specs_string[2]] = (specs_string[2], fr'({instructions})\b');
token_specs[specs_string[3]] = (specs_string[3], fr'[\s]*(?:{registers})\b');
token_specs[specs_string[4]] = (specs_string[4], r'[\s]*,');
token_specs[specs_string[5]] = (specs_string[5], r'\s*([0-9a-fA-F]{2});');
token_specs[specs_string[6]] = (specs_string[6], r"'(?:\\[ntr]|\\'|[^\\'])'");
token_specs[specs_string[7]] = (specs_string[7], r'[\s]{0,}(;.*)|[\s]{0,}(;)');
token_specs[specs_string[8]] = (specs_string[8], r'[^";]*');
token_specs[specs_string[9]] = (specs_string[9], r'-?(\d+\.\d+|\.\d+|\d+\.)');
token_specs[specs_string[10]] = (specs_string[10], r'\(');
token_specs[specs_string[11]] = (specs_string[11], r'\)');
token_specs[specs_string[12]] = (specs_string[12], r'\s+');
token_specs[specs_string[13]] = (specs_string[13], r'[^\s]+');

token_regex_str = "|"
for pair in enumerate(specs_string):
  sub_pair = token_specs[pair[1]]
  token_regex_str = token_regex_str + "".join('(?P<%s>%s)' % (sub_pair[0], sub_pair[1]))
  token_regex_str = token_regex_str + "|"
token_regex = re.compile(token_regex_str, flags=re.IGNORECASE)

re_str = r'^(?P<DIRECTIVE>'+token_specs['DIRECTIVE'][1]+'\s+(?P<STRING>'+token_specs['STRING'][1]+')\s*(?P<COMMENT>'+token_specs['COMMENT'][1]+'))$'
print (re_str)
label_directive_regex = re.compile(re_str, flags=re.IGNORECASE)

re_str = r'^(?P<COMMENT>' + token_specs['COMMENT'][1] + r')$'
print (re_str)
comment_regex = re.compile(re_str)

re_str = r'^(?P<LABEL_DEFINITION>' + token_specs['LABEL_DEFINITION'][1] + ')$'
print (re_str)
code_label_definition_regex = re.compile(re_str)

re_str = r'^(?P<INSTRUCTION>' + instructions + r').*(?P<COMMENT>' + token_specs['COMMENT'][1] + r')$'
print (re_str)
instruction_and_comment_regex = re.compile(re_str)

def lex(text: str) -> List[List[Tuple[str, str]]]:
    tokens = initial_lex(text)
    return delete_whitespace(replace_unknowns_with_labels(tokens, find_labels(tokens)))

def initial_lex(text: str) -> List[List[Tuple[str, str]]]:
    tokens = []
    for line in text.splitlines():
        subtokens = []
        for match in token_regex.finditer(line):
            token_type = match.lastgroup
            token_value = match.group()
            subtokens.append((token_type, token_value))
        tokens.append(subtokens)
    return tokens

def find_labels(tokens: List[List[Tuple[str, str]]]) -> List[str]:
    labels = []
    for sub_tokens in tokens:
        for token_type, token_value in sub_tokens:
            if token_type == 'LABEL_DEFINITION':
                label_name = token_value.rstrip(':')
                labels.append(label_name)
    return labels

def replace_unknowns_with_labels(
        tokens: List[List[Tuple[str, str]]], 
        labels: List[str]
    ) -> List[List[Tuple[str, str]]]:
    new_tokens = []
    for sub_tokens in tokens:
        new_subtokens = []
        for token_type, token_value in sub_tokens:
            if token_type == 'UNKNOWN' and token_value in labels:
                token_type = 'LABEL'
            new_subtokens.append((token_type, token_value))
        new_tokens.append(new_subtokens)
    return new_tokens

def delete_whitespace(
        tokens: List[List[Tuple[str, str]]]
    ) -> List[List[Tuple[str, str]]]:
    new_tokens = []
    for sub_tokens in tokens:
        new_subtokens = [
            (token_type, token_value) 
            for token_type, token_value in sub_tokens 
            if token_type != 'WHITESPACE'
        ]
        if len(new_subtokens) > 0:
            new_tokens.append(new_subtokens)
    return new_tokens

def count_tokens(tokens: List[List[Tuple[str, str]]]) -> Dict[str, int]:
    token_count = defaultdict(int)
    for subtokens in tokens:
        for token_type, _ in subtokens:
            token_count[token_type] += 1
    return dict(token_count)
