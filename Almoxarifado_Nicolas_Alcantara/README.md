# Almoxarifado simples - Nicolas Alcantara

Site em Python (FastAPI), com HTML e registros em arquivos JSON. A lógica está em `repositorio.py` e as rotas em `app.py`.

## Executar no VS Code

1. Abra esta pasta no terminal.
2. Rode `pip install -r requirements.txt`.
3. Rode `python app.py`.
4. Abra http://127.0.0.1:5000 .

**Acesso de teste:** administrador `admin` / `admin123`; operador `operador` / `operador123`. São logins demonstrativos e devem ser trocados antes de qualquer uso real. Senhas ficam em hash PBKDF2.

## Funcionalidades

- Operador: consultar, cadastrar, editar, registrar entrada e saída, ver histórico.
- Administrador: todas essas opções, excluir produtos e criar usuários.
- O sistema exige autenticação em todas as rotas protegidas, guarda data/hora e login em cada movimento, atualiza o saldo e proíbe saída superior ao estoque.
- Produtos: filtro por nome e data de cadastro, com 5 produtos por página.
- Exclusão lógica: o produto sai da lista, mas o histórico permanece.
- Não se muda saldo diretamente pela edição: apenas por movimentação.

## Testes e documentação

`python -m unittest discover -s testes -v` roda os testes. O plano está em `docs/plano_testes.docx`, os resultados em `resultados.docx` e as três evidências em `docs/testes`.

## Git

O ZIP tem branches `main` e `Nicolas-Alcantara`. Para entregar, faça push das branches ao repositório solicitado pelo professor e abra um Pull Request da branch `Nicolas-Alcantara` para a `main`. Se for usado um repositório já existente da escola, clone-o e copie apenas o código (sem a pasta `.git`).

Este é um protótipo para execução local; o arquivo JSON não oferece proteção adequada para vários usuários concorrentes.
