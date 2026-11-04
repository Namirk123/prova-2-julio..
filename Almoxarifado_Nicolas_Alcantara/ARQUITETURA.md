# Organização do sistema de Nicolas

- `app.py`: páginas web, login e permissões para acessar rotas.
- `repositorio.py`: classe `Repositorio`, que executa cadastro, atualização e movimentação com os dados JSON.
- `dados/estoque.json`: tabela simulada com produtos e histórico.
- `dados/usuarios.json`: perfis e senhas protegidas por hash.
- `templates/`: apresentação HTML, sem cálculos de estoque.
- `testes/`: verificações isoladas do armazenamento, usando pasta temporária.

**Fluxo:** login → validação do perfil → pedido do usuário → regra de estoque → gravação do JSON → resultado na página.

**Regras:** saída maior que saldo é rejeitada antes da gravação. Operador não acessa exclusão ou cadastro de usuário. Histórico guarda responsável e horário. Para esta tarefa local, um único arquivo de dados simplifica o aprendizado.
