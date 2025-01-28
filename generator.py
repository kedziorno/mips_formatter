import re
from typing import List, Tuple
from collections import defaultdict

import lexer

tab_len = 2

def generate(tokens: List[List[Tuple[str, str]]]) -> List[str]:
    # For now, the order of horizontal -> vertical is important.
    tokens = add_horizontal_whitespace(tokens) 
    tokens = add_vertical_whitespace(tokens)
    return tokens_to_text(tokens)

def add_horizontal_whitespace(tokens: List[List[Tuple[str, str]]]) -> List[List[Tuple[str, str]]]:
    new_tokens = []
    # Do this first
    for subtokens in tokens:
        new_subtokens = []
        prev_token_type = None
        prev_token_value = None
        prev_prev_token_type = None
        for token_type, token_value in subtokens:
            if token_type == 'INSTRUCTION':
                new_subtokens.append(('WHITESPACE', ' ' * tab_len))
            if prev_token_type == 'INSTRUCTION':
                new_subtokens.append(('WHITESPACE', ' ' * (tab_len - len(prev_token_value))))
            if prev_token_type == 'COMMA' or prev_token_type == 'LABEL_DEFINITION' and not token_type == 'DIRECTIVE' or prev_token_type == 'DIRECTIVE' and not prev_prev_token_type == 'LABEL_DEFINITION' or prev_token_type == 'INSTRUCTION':
                #print ("bbb")
                new_subtokens.append(('WHITESPACE', ' '))

            new_subtokens.append((token_type, token_value))
            prev_prev_token_type = prev_token_type
            prev_token_type = token_type
            prev_token_value = token_value
        new_tokens.append(new_subtokens)

    new_tokens = align_right_side_comments(new_tokens)
    new_tokens = align_data_section(new_tokens)
    new_tokens = align_inline_comments(new_tokens)
    return new_tokens

def align_data_section(tokens: List[List[Tuple[str, str]]]) -> List[List[Tuple[str, str]]]:
    return align_data_comments(align_data_code(tokens))

def align_data_code(tokens: List[List[Tuple[str, str]]]) -> List[List[Tuple[str, str]]]:
    new_tokens = tokens
    longest_len = 0
    for subtokens in new_tokens:
        if len(subtokens) < 5 or not (subtokens[1][0] == 'LABEL_DEFINITION'):
            continue
        longest_len = max(longest_len, len(subtokens[1][1]))

    multiplier = 0
    while longest_len > tab_len * multiplier:
        multiplier += 1

    for i, subtokens in enumerate(tokens):
        if len(subtokens) < 5 or not (subtokens[1][0] == 'LABEL_DEFINITION'):
            continue
        #print (f"subtokens - {len(subtokens)} - {subtokens}")    
        #new_tokens[i].insert(0, ('WHITESPACE', ' ' * (multiplier * tab_len - len(subtokens[1][1]))))
        #new_tokens[i].insert(1, ('WHITESPACE', ' ' * (multiplier * tab_len - len(subtokens[1][1]))))
        new_tokens[i].pop(2)
        #new_tokens[i].insert(2, ('WHITESPACE', ' ' * (multiplier * tab_len - len(subtokens[1][1]))))
        #new_tokens[i].insert(3, ('WHITESPACE', ' ' * (multiplier * tab_len - len(subtokens[1][1]))))
        #new_tokens[i].insert(4, ('WHITESPACE', ' ' * (multiplier * tab_len - len(subtokens[1][1]))))
        #new_tokens[i].insert(5, ('WHITESPACE', ' ' * (multiplier * tab_len - len(subtokens[1][1]))))
        #new_tokens[i].insert(6, ('WHITESPACE', ' ' * (multiplier * tab_len - len(subtokens[1][1]))))
        #new_tokens[i].insert(7, ('WHITESPACE', ' ' * (multiplier * tab_len - len(subtokens[1][1]))))
        #new_tokens[i].insert(8, ('WHITESPACE', ' ' * (multiplier * tab_len - len(subtokens[1][1]))))
        #new_tokens[i].insert(9, ('WHITESPACE', ' ' * (multiplier * tab_len - len(subtokens[1][1]))))
        new_tokens[i].insert(2, ('WHITESPACE', ' ' * ((multiplier + 1) * tab_len - len(subtokens[1][1]) - len(subtokens[4][1]))))
        #print (f"newtokens - {len(new_tokens)} - {new_tokens[i]}")
        
    return new_tokens

def align_data_comments(tokens: List[List[Tuple[str, str]]]) -> List[List[Tuple[str, str]]]:
    new_tokens = tokens
    longest_len = 0
    for subtokens in new_tokens:
        ldr_match = lexer.label_directive_regex.match(tokens_to_line(subtokens))
        if not ldr_match:
            continue
        longest_len = max(longest_len, sum(len(token_value) for _, token_value in subtokens[:-1]))

    multiplier = 0
    while longest_len > tab_len * multiplier:
        multiplier += 1

    for i, subtokens in enumerate(tokens):
        if not lexer.label_directive_regex.match(tokens_to_line(subtokens)):
            continue
        if (len(new_tokens[i]) == 8):
          #new_tokens[i].pop(2)
          #new_tokens[i].insert(2, ('WHITESPACE', ' '));
          #new_tokens[i].insert(12, ('aaa', 'bbb'));
          new_tokens[i].insert(5, ('WHITESPACE', ' ' * (tab_len * multiplier - sum(len(token_value) for _, token_value in subtokens[:-1]))))
        if (len(new_tokens[i]) == 13):
          #new_tokens[i].pop(11)
          #new_tokens[i].insert(12, ('ccc', 'ddd'));
          #for i in subtokens[:-1]:
          #  print (f"newtokens - {len(subtokens[i][:-1])} - {subtokens[i][:-1]}")
          #print (f"ssss - {subtokens[:-1]}")
          new_tokens[i].insert(11, ('WHITESPACE', ' ' * (tab_len * multiplier - sum(len(token_value) for _, token_value in subtokens[:-1]))))
        #print (f"newtokens - {len(new_tokens[i])} - {new_tokens[i]}")
        
    return new_tokens

def align_inline_comments(tokens: List[List[Tuple[str, str]]]) -> List[List[Tuple[str, str]]]:
    new_tokens = tokens
    for i, subtokens in enumerate(tokens):
        if not (lexer.comment_regex.match(tokens_to_line(subtokens)) and i + 1 < len(tokens) and not  lexer.code_label_definition_regex.match(tokens_to_line(tokens[i + 1]))):
            continue
        print (f"align_inline_comments - {i} {len(subtokens)} - {subtokens}")    
        
        new_tokens[i].insert(0, ('WHITESPACE', ' ' * tab_len))
    return new_tokens

def align_right_side_comments(tokens: List[List[Tuple[str, str]]]) -> List[List[Tuple[str, str]]]:
    new_tokens = tokens
    longest_len = 0
    for subtokens in tokens:
        if (len(subtokens) == 15 or len(subtokens) == 10 or len(subtokens) == 8):
            print (f"align_inline_comments - {len(subtokens)} - {subtokens}")    
            #print (subtokens[2][0])
            #print (subtokens[len(subtokens)-2][0])
            if not (len(subtokens) > 1 and subtokens[2][0] == 'INSTRUCTION' and subtokens[len(subtokens)-2][0] == 'COMMENT'):
                continue
            line_len = 1 + sum(len(token_value) for _, token_value in subtokens[:-1])
            longest_len = max(longest_len, line_len)

    multiplier = 0
    while longest_len > tab_len * multiplier:
        multiplier += 1
    
    for i, subtokens in enumerate(tokens):
        if not (len(subtokens) > 1 and subtokens[2][0] == 'INSTRUCTION' and subtokens[len(subtokens) - 2][0] == 'COMMENT'):
            continue
        #print (subtokens[2][0])
        #print (subtokens[len(subtokens)-2][0])
        line_len = sum(len(token_value) for _, token_value in subtokens[:-1])
        #print (subtokens[:-1])
        #print (('WHITESPACE', ' ' * (multiplier * tab_len - line_len)))
        new_tokens[i].insert(len(subtokens[:-2]), ('WHITESPACE', ' ' * (multiplier * tab_len - line_len)))
        #print (f"align_inline_comments1 - {len(new_tokens[i])} - {new_tokens[i]}")    
        
    return new_tokens

def add_vertical_whitespace(tokens: List[List[Tuple[str, str]]]) -> List[List[Tuple[str, str]]]:
    new_tokens = []
    longest_len = 0
    for i, subtokens in enumerate(tokens):
        print (f"qwert - {len(subtokens)} - {subtokens}")
        if (i > 0 and 
            len(subtokens) > 1 and
            (subtokens[1][0] == 'COMMENT' or subtokens[0][0] == 'COMMENT') and 
            len(tokens[i - 1]) > 1 and
            tokens[i - 1][0][0] == 'INSTRUCTION'):
            print #new_tokens.append([('WHITESPACE', '')])
        new_tokens.append(subtokens)
        print (f"add_vertical_whitespace111 - {i} - {len(new_tokens[i])} - {new_tokens[i]}")    

        for subtokens in new_tokens:
            if len(subtokens) < 2 or not (subtokens[2][0] == 'INSTRUCTION'):
                continue
            #print ("ll "+subtokens[2][1])
            longest_len = max(longest_len, len(subtokens[2][1]))

        multiplier = 0
        while longest_len > tab_len * multiplier:
            multiplier += 1


        if (i > 0 and 
            len(subtokens) > 1 and
            len(tokens[i - 1]) > 1 and
            ((tokens[i-1][1][0] == 'LABEL_DEFINITION'))):
            print ("subtoken333 " + tokens[i-1][2][1])
    
            #new_tokens[i].pop(2)
            new_tokens[i].insert(3, ('WHITESPACE', '|' * ((multiplier+1) * tab_len - len(tokens[i][2][1]))))
            print (f"add_vertical_whitespace444 - {len(new_tokens[i])} - {new_tokens[i]}")    
        
        if (i > 0 and 
            len(subtokens) > 1 and
            len(tokens[i - 2]) > 1 and len(tokens[i - 1]) > 1 and
            ((tokens[i - 1][2][0] == 'INSTRUCTION') or (tokens[i - 2][1][0] == 'LABEL_DEFINITION'))):
            print ("subtoken " + tokens[i][2][1])
    
            #new_tokens[i].pop(2)
            new_tokens[i].insert(3, ('WHITESPACE', '-' * ((multiplier+1) * tab_len - len(tokens[i][2][1]))))
            print (f"add_vertical_whitespace222 - {len(new_tokens[i])} - {new_tokens[i]}")    


        if len(subtokens) > 0 and is_code_label_definition(subtokens):
            j = i
            while (j > -1 and
                   len(tokens[j]) > 0 and
                   (tokens[j][1][0] == 'COMMENT' or
                    tokens[j][1][0] == 'DIRECTIVE' or
                    is_code_label_definition(tokens[j]))):
                j -= 1
            new_tokens.insert(len(new_tokens) - (i - j), [('WHITESPACE', '+')])
        print (f"add_vertical_whitespace333 - {len(new_tokens[i])} - {new_tokens[i]}")    
    return new_tokens

def is_code_label_definition(tokens: List[List[Tuple[str, str]]]) -> bool:
    return tokens[0][0] == 'LABEL_DEFINITION' and not any(token[0] in [
        'DIRECTIVE', 'INSTRUCTION', 'REGISTER', 'FLOAT', 'INTEGER',
        'CHAR', 'STRING', 'LABEL', 'COMMA', 'LBRACKET', 'RBRACKET'
    ] for token in tokens)

def tokens_to_text(tokens: List[List[Tuple[str, str]]]) -> List[str]:
    lines = []
    for subtokens in tokens:
        line = ''
        for _, token_value in subtokens:
            line += token_value
        lines.append(line)
    return lines

def tokens_to_line(tokens: List[List[Tuple[str, str]]]) -> str:
    line = ''
    for _, token_value in tokens:
        line += token_value
    return line

    
    
