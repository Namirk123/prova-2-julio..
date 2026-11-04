"""Leitura dos arquivos JSON e regras básicas do almoxarifado."""
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path


def abrir(caminho, padrao):
    if not Path(caminho).exists():
        return padrao
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def guardar(caminho, conteudo):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_suffix('.tmp')
    temporario.write_text(json.dumps(conteudo, ensure_ascii=False, indent=2), encoding='utf-8')
    temporario.replace(caminho)


class Repositorio:
    def __init__(self, pasta='dados'):
        self.pasta = Path(pasta)
        self.arquivo = self.pasta / 'estoque.json'
        self.usuarios = self.pasta / 'usuarios.json'

    def dados(self):
        return abrir(self.arquivo, {'produtos': [], 'movimentacoes': []})

    def pessoas(self):
        return abrir(self.usuarios, [])

    def autenticar(self, login, senha):
        for pessoa in self.pessoas():
            if pessoa['login'] == login and pessoa.get('ativo', True):
                gerada = hashlib.pbkdf2_hmac('sha256', senha.encode(), pessoa['salt'].encode(), 100000).hex()
                if gerada == pessoa['sal']:
                    return pessoa
        return None

    def usuario(self, identificador):
        return next((p for p in self.pessoas() if p['id'] == identificador and p.get('ativo', True)), None)

    def novo_usuario(self, login, senha, perfil):
        pessoas = self.pessoas()
        if not login or not senha or perfil not in ('admin', 'operador'):
            raise ValueError('Preencha login, senha e perfil válido.')
        if any(p['login'] == login for p in pessoas):
            raise ValueError('Login já cadastrado.')
        salt = os.urandom(8).hex()
        sal = hashlib.pbkdf2_hmac('sha256', senha.encode(), salt.encode(), 100000).hex()
        pessoas.append(dict(id=max([p['id'] for p in pessoas], default=0) + 1,
                            login=login, perfil=perfil, salt=salt, sal=sal, ativo=True))
        guardar(self.usuarios, pessoas)

    def produtos(self, nome='', data='', pagina=1):
        produtos = [p for p in self.dados()['produtos'] if p.get('ativo', True)]
        if nome:
            produtos = [p for p in produtos if nome.lower() in p['nome'].lower()]
        if data:
            produtos = [p for p in produtos if p['data_cadastro'][:10] == data]
        produtos.sort(key=lambda p: p['id'])
        total = max(1, (len(produtos) + 4) // 5)
        pagina = max(1, min(pagina, total))
        return produtos[(pagina - 1) * 5:pagina * 5], total, pagina

    def cadastrar(self, nome, quantidade, responsavel):
        nome = nome.strip()
        quantidade = int(quantidade)
        if not nome or quantidade < 0:
            raise ValueError('Informe um nome e quantidade não negativa.')
        dados = self.dados()
        identificador = max([p['id'] for p in dados['produtos']], default=0) + 1
        dados['produtos'].append(dict(id=identificador, nome=nome, quantidade=0,
                                     data_cadastro=datetime.now().isoformat(timespec='seconds'), ativo=True))
        guardar(self.arquivo, dados)
        if quantidade:
            self.movimentar(identificador, 'entrada', quantidade, responsavel)
        return identificador

    def produto(self, identificador, dados=None):
        dados = dados or self.dados()
        p = next((p for p in dados['produtos'] if p['id'] == int(identificador) and p.get('ativo', True)), None)
        if p is None:
            raise ValueError('Produto não encontrado.')
        return p

    def alterar(self, identificador, nome):
        if not nome.strip():
            raise ValueError('Informe o nome.')
        dados = self.dados()
        self.produto(identificador, dados)['nome'] = nome.strip()
        guardar(self.arquivo, dados)

    def excluir(self, identificador):
        dados = self.dados()
        self.produto(identificador, dados)['ativo'] = False
        guardar(self.arquivo, dados)

    def movimentar(self, identificador, tipo, quantidade, responsavel):
        quantidade = int(quantidade)
        if tipo not in ('entrada', 'saida') or quantidade <= 0:
            raise ValueError('Informe tipo e quantidade válida.')
        dados = self.dados()
        p = self.produto(identificador, dados)
        if tipo == 'saida' and quantidade > p['quantidade']:
            raise ValueError(f"Saída não permitida: estoque insuficiente. Disponível: {p['quantidade']}. Solicitado: {quantidade}.")
        p['quantidade'] += quantidade if tipo == 'entrada' else -quantidade
        dados['movimentacoes'].append(dict(id=len(dados['movimentacoes']) + 1, produto_id=p['id'],
                      produto=p['nome'], tipo=tipo, quantidade=quantidade,
                      usuario=responsavel, data_hora=datetime.now().isoformat(timespec='seconds')))
        guardar(self.arquivo, dados)

    def historico(self, nome='', data=''):
        registro = self.dados()['movimentacoes']
        return [m for m in reversed(registro) if nome.lower() in m['produto'].lower()
                and (not data or m['data_hora'][:10] == data)]
