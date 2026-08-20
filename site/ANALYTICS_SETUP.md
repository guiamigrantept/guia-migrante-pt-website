# Analytics e feedback — preparado, não ativado

A V12 não envia analytics nem feedback para um servidor.

## Analytics
Se for ativado no futuro:
- preferir solução sem cookies e sem perfis publicitários;
- atualizar `privacidade.html` / `en/privacidade.html` antes da ativação;
- documentar fornecedor, finalidade, dados processados e retenção;
- testar se o carregamento do site continua rápido em mobile.

## Feedback
O interface central de feedback deve ser ativado apenas quando existir um endpoint real e uma política definida.
Requisitos mínimos:
- não pedir documentos de imigração, passwords ou códigos;
- permitir feedback anónimo;
- recolher apenas página, voto/comentário opcional e timestamp;
- aplicar proteção contra spam;
- definir prazo de retenção;
- explicar o tratamento na Política de Privacidade.

Não inserir tokens, endpoints ou e-mails privados diretamente no código público sem necessidade.
