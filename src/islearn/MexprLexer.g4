lexer grammar MexprLexer;

BRAOP : '{' -> pushMode(VAR_DECL) ;

OPTOP : '[' -> pushMode(OPTIONAL) ;

TEXT : (~ [{[]) + ;

NL : '\n' + -> skip ;

mode VAR_DECL;
BRACL : '}' -> popMode ;
ID: ID_LETTER (ID_LETTER | DIGIT) * ;
fragment ID_LETTER : 'a'..'z'|'A'..'Z' | [_\-.] ;
fragment DIGIT : '0'..'9' ;
GT: '>' ;
LT: '<' ;
WS : [ \t\n\r]+ -> skip ;

mode OPTIONAL;
OPTCL : ']' -> popMode ;
OPTTXT : (~ ']') + ;