# Analytics e feedback — estado operacional

Atualizado em 24/08/2026.

## Analytics
O Guia Migrante PT usa medição própria, limitada e sem cookies através de `/api/analytics`.

São registados apenas:
- tipo de evento (`page_view`, envio concluído do formulário ou clique numa fonte oficial);
- caminho da página;
- idioma;
- hostname de origem externa, quando o navegador o fornece;
- hostname da fonte oficial clicada;
- parâmetros UTM `source`, `medium` e `campaign`, quando existirem no URL.

Não são guardados pela aplicação:
- endereço IP;
- user-agent;
- cookies publicitários;
- identificadores persistentes de utilizador ou dispositivo;
- URL completo do referenciador;
- conteúdo das mensagens;
- assunto da mensagem dentro do sistema de analytics.

Global Privacy Control e Do Not Track são respeitados pelo JavaScript de medição.
Os eventos de analytics são eliminados após 90 dias.

A área protegida `/admin-estatisticas.html` mostra apenas agregados úteis para avaliar páginas, idiomas, campanhas e conversões.

## Feedback / contacto
O canal “Fale com o Guia” está ativo em `/contactos.html` e nas versões localizadas.

Regras:
- nome e email são opcionais;
- não pedir documentos de imigração, passwords ou códigos;
- conteúdo limitado a 4000 caracteres;
- proteção contra spam e duplicados;
- mensagens retidas até 180 dias;
- gestão através da área protegida `/admin-mensagens.html`.

## Segurança e privacidade
Não inserir tokens, chaves de administração, endpoints privados ou emails privados no código público.
A Política de Privacidade deve permanecer alinhada com este ficheiro sempre que o tratamento de dados mudar.
