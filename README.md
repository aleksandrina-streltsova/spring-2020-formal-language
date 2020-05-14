[![Build Status](https://travis-ci.com/aleksandrina-streltsova/spring-2020-formal-language.svg?branch=dev)](https://travis-ci.com/aleksandrina-streltsova/spring-2020-formal-language)
# spring-2020-formal-language
Реализация графовой базы данных в рамках учебного проекта по теории формальных языков.

## Сборка на Linux
    pip install -r requirements.txt
## Запуск тестов
    pytest 
## Язык запросов к графам
### Синтаксис
##### Основной синтаксис
```
script       -> EPS | stmt SEMI script
stmt         -> KW_CONNECT KW_TO STRING | KW_LIST | select_stmt | NT_NAME OP_EQ pattern
select_stmt  -> KW_SELECT obj_expr KW_FROM STRING KW_WHERE where_expr 
obj_expr     -> vs_info | KW_COUNT vs_info | KW_EXISTS vs_info 
where_expr   -> LBRACE v_expr RBRACE pattern OP_ARROW LBRACE v_expr RBRACE
vs_info      -> IDENT | LBRACE IDENT COMMA IDENT RBRACE
v_expr       -> IDENT | UNDERSCORE | IDENT DOT KW_ID OP_EQ INT
```
##### Регулярные выражения
```
pattern      -> alt_elem | alt_elem OP_OR pattern
alt_elem     -> seq | KW_EPS
seq          -> seq_elem | seq_elem seq
seq_elem     -> prim_pattern | prim_pattern OP_STAR | prim_pattern OP_PLUS | prim_pattern OP_QUEST
prim_pattern -> IDENT | NT_NAME | LBRACE pattern RBRACE
```
### Токены
##### Ключевые слова
```
KW_CONNECT = 'connect'
KW_TO = 'to'
KW_LIST = 'list'
KW_SELECT = 'select'
KW_FROM = 'from'
KW_WHERE = 'where'
KW_COUNT = 'count'
KW_EXISTS = 'exists'
KW_ID = 'id'
KW_EPS = 'eps'
```
##### Разделители
```
SEMI=';'
COMMA = ','
LBRACE = '('
RBRACE = ')'
UNDERSCORE = '_'
DOT = '.'
```
##### Литералы
```
STRING = '"'([A-Za-z]|[0-9]|('-'|' '|'/'|'.'|','|'_'))*'"' 
INT = 0|[1-9][0-9]*
NT_NAME = [A-Z]+([1-9][0-9]*)?
IDENT = [a-z]+
```
##### Операторы
```
OP_EQ = '='
OP_ARROW = '->'
OP_OR = '|'
OP_STAR = '*'
OP_PLUS = '+'
OP_QUEST = '?'
```
### Примеры
загрузка графа:
```
connect to "tests/graph.txt";
```
вывод списка всех загруженных графов:
```
list;
```
добавление правила в грамматику:
```
S = S a S b | eps;
```
число достижимых пар вершин графа:
```
select count (u, v) from "tests/graph.txt" where (u) S -> (v);
```
проверка существования пути между двумя вершинами:
```
select exists (u, v) from "tests/graph.txt" where (u.id = 1) S -> (v.id = 2);
```
