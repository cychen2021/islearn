grammar IslaLanguage;

start: constDecl? formula;

constDecl: 'const' ID ':' VAR_TYPE ';' ;

formula:
    'forall' (boundVarType=(VAR_TYPE | NONTERMINAL_PH)) (varId=ID) ?            ('in' (inId=ID | inVarType=VAR_TYPE)) ? ':' formula  # Forall
  | 'exists' (boundVarType=(VAR_TYPE | NONTERMINAL_PH)) (varId=ID) ?            ('in' (inId=ID | inVarType=VAR_TYPE)) ? ':' formula  # Exists
  | 'forall' (boundVarType=(VAR_TYPE | NONTERMINAL_PH)) (varId=ID) ? '=' STRING ('in' (inId=ID | inVarType=VAR_TYPE)) ? ':' formula  # ForallMexpr
  | 'exists' (boundVarType=(VAR_TYPE | NONTERMINAL_PH)) (varId=ID) ? '=' STRING ('in' (inId=ID | inVarType=VAR_TYPE)) ? ':' formula  # ExistsMexpr
  | 'exists' 'int' ID ':' formula                   # ExistsInt
  | 'forall' 'int' ID ':' formula                   # ForallInt
  | 'not' formula                                   # Negation
  | formula 'and' formula                           # Conjunction
  | formula 'or' formula                            # Disjunction
  | formula 'xor' formula                           # ExclusiveOr
  | formula 'implies' formula                       # Implication
  | formula 'iff' formula                           # Equivalence
  | ID '(' predicateArg (',' predicateArg) * ')'    # PredicateAtom
  | sexpr                                           # SMTFormula
  | '(' formula ')'                                 # ParFormula
  ;

sexpr:
    'true'                                  # SexprTrue
  | 'false'                                 # SexprFalse
  | INT                                     # SexprNum
  | ID                                      # SexprId
  | XPATHEXPR                               # SexprXPathExpr
  | VAR_TYPE                                # SexprFreeId
  | STRING                                  # SexprStr
  | NONTERMINAL_PH                          # SexprNonterminalStringPh
  | STRING_PH                               # SexprStringPh
  | DSTRINGS_PH                             # SexprDisjStringsPh
  | ('=' | GEQ | LEQ | GT | LT | 're.+' | 're.*' | 're.++' | 'str.++' | DIV | MUL | PLUS | MINUS)
                                            # SexprOp
  | op=('re.+' | 're.*') '(' sexpr ')'      # SexprPrefix
  | sexpr op=('re.++' | 'str.++') sexpr     # SexprInfixReStr
  | sexpr op=(PLUS | MINUS) sexpr           # SexprInfixPlusMinus
  | sexpr op=(MUL | DIV) sexpr              # SexprInfixMulDiv
  | sexpr op=('=' | GEQ | LEQ | GT | LT) sexpr # SexprInfixEq
  | '(' sexpr ')'                           # SepxrParen
  | '(' op=sexpr sexpr + ')'                # SepxrApp
  ;

predicateArg: ID | VAR_TYPE | INT | STRING | XPATHEXPR | NONTERMINAL_PH | STRING_PH | DSTRINGS_PH ;

XPATHEXPR: (ID | VAR_TYPE) XPATHSEGMENT + ;

fragment XPATHSEGMENT:
      DOT VAR_TYPE
    | DOT VAR_TYPE BROP INT BRCL
    | TWODOTS VAR_TYPE
    ;

NONTERMINAL_PH: '<?NONTERMINAL>' ;
STRING_PH: '<?STRING>' ;
DSTRINGS_PH: '<?DSTRINGS>' ;

VAR_TYPE : LT ID GT ;

STRING: '"' (ESC|.) *? '"';
ID: ID_LETTER (ID_LETTER | DIGIT) * ;
INT : DIGIT+ ;
ESC : '\\' [btnr"\\] ;

DOT : '.' ;
TWODOTS : '..' ;
BROP : '[' ;
BRCL : ']' ;

DIV: '/' ;
MUL: '*' ;
PLUS: '+' ;
MINUS: '-' ;
GEQ: '>=' ;
LEQ: '<=' ;
GT: '>' ;
LT: '<' ;

WS : [ \t\n\r]+ -> skip ;
LINE_COMMENT : '#' .*? '\n' -> skip ;

fragment ID_LETTER : 'a'..'z'|'A'..'Z' | [_\-.^] ;
fragment DIGIT : '0'..'9' ;
