grammar query;
// parser rules:
script : stmt* EOF ;

stmt : (KW_CONNECT KW_TO STRING
      | KW_CONNECT KW_TO KW_DATABASE STRING
      | KW_LIST STRING?
      | select_stmt
      | NT_NAME OP_EQ pattern)
      SEMI ;

select_stmt : KW_SELECT obj_expr KW_FROM STRING KW_WHERE where_expr ;

obj_expr : vs_info | KW_COUNT vs_info | KW_EXISTS vs_info ;

where_expr : LBRACE v_expr RBRACE pattern OP_ARROW LBRACE v_expr RBRACE ;

vs_info : IDENT | LBRACE IDENT COMMA IDENT RBRACE ;

v_expr : IDENT | UNDERSCORE | IDENT DOT KW_ID OP_EQ INT ;

pattern : alt_elem | alt_elem OP_OR pattern ;

alt_elem : seq | KW_EPS ;

seq : seq_elem+ ;

seq_elem : prim_pattern (OP_STAR | OP_PLUS | OP_QUEST)? ;

prim_pattern : IDENT | NT_NAME | LBRACE pattern RBRACE ;

// lexer rules:

WS : [ \r\n\t] + -> skip ;

KW_CONNECT : 'connect' ;
KW_TO : 'to' ;
KW_LIST : 'list' ;
KW_SELECT : 'select' ;
KW_FROM : 'from' ;
KW_WHERE : 'where' ;
KW_COUNT : 'count' ;
KW_EXISTS : 'exists' ;
KW_ID : 'id' ;
KW_EPS : 'eps' ;
KW_DATABASE : 'database' ;

SEMI : ';' ;
COMMA : ',' ;
LBRACE : '(' ;
RBRACE : ')' ;
UNDERSCORE : '_' ;
DOT : '.' ;

STRING : '"'([a-zA-Z]|[0-9]|('-'|' '|'/'|'.'|','|'_'))*'"' ;
INT : '0' | [1-9][0-9]* ;
NT_NAME : [A-Z]+([1-9][0-9]*)? ;
IDENT : [a-z]+ ;

OP_EQ : '=' ;
OP_ARROW : '->' ;
OP_OR : '|' ;
OP_STAR : '*' ;
OP_PLUS : '+' ;
OP_QUEST : '?' ;