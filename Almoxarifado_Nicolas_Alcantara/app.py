"""Site de estoque de Nicolas. Execute: python app.py"""
import os
import secrets
from pathlib import Path
from urllib.parse import quote
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from repositorio import Repositorio

BASE = Path(__file__).resolve().parent
banco = Repositorio(BASE / 'dados')
app = FastAPI(title='Estoque | Nicolas')
app.add_middleware(SessionMiddleware, secret_key=os.environ.get('SECRET_KEY') or secrets.token_hex(32))
telas = Jinja2Templates(directory=BASE / 'templates')


def atual(req):
    return banco.usuario(req.session.get('id'))


def checar(req, admin=False):
    pessoa = atual(req)
    if pessoa is None:
        return RedirectResponse('/login', status_code=303)
    if admin and pessoa['perfil'] != 'admin':
        raise HTTPException(403, 'Acesso exclusivo ao administrador')


def tela(req, arquivo, **dados):
    return telas.TemplateResponse(req, arquivo, {'pessoa': atual(req), 'aviso': req.query_params.get('aviso',''), **dados})


def voltar(caminho, aviso=''):
    return RedirectResponse(caminho + (('?aviso=' + quote(aviso)) if aviso else ''), status_code=303)


@app.get('/login')
def login(req: Request):
    return tela(req, 'login.html')


@app.post('/login')
async def entrar(req: Request):
    f = await req.form()
    pessoa = banco.autenticar(str(f.get('login','')), str(f.get('senha','')))
    if pessoa:
        req.session.clear()
        req.session['id'] = pessoa['id']
        return voltar('/')
    return voltar('/login', 'Usuário ou senha inválidos')


@app.post('/sair')
def sair(req: Request):
    req.session.clear()
    return voltar('/login')


@app.get('/')
def inicio(req: Request):
    if resposta := checar(req): return resposta
    try: pagina = int(req.query_params.get('pagina', '1'))
    except ValueError: pagina = 1
    nome = req.query_params.get('nome', '')
    data = req.query_params.get('data', '')
    produtos, paginas, pagina = banco.produtos(nome, data, pagina)
    return tela(req, 'inicio.html', produtos=produtos, paginas=paginas, pagina=pagina, nome=nome, data=data)


@app.post('/cadastrar')
async def cadastrar(req: Request):
    if resposta := checar(req): return resposta
    f = await req.form()
    try:
        banco.cadastrar(str(f.get('nome','')), int(f.get('quantidade', 0)), atual(req)['login'])
        return voltar('/', 'Produto cadastrado')
    except (ValueError, TypeError) as erro:
        return voltar('/', str(erro))


@app.post('/renomear/{identificador}')
async def renomear(req: Request, identificador: int):
    if resposta := checar(req): return resposta
    f = await req.form()
    try: banco.alterar(identificador, str(f.get('nome','')))
    except ValueError as erro: return voltar('/', str(erro))
    return voltar('/', 'Nome atualizado')


@app.post('/movimentar/{identificador}')
async def movimentar(req: Request, identificador: int):
    if resposta := checar(req): return resposta
    f = await req.form()
    try:
        banco.movimentar(identificador, str(f.get('tipo','')), int(f.get('quantidade', 0)), atual(req)['login'])
        return voltar('/', 'Movimentação registrada')
    except (ValueError, TypeError) as erro:
        return voltar('/', str(erro))


@app.post('/excluir/{identificador}')
def excluir(req: Request, identificador: int):
    if resposta := checar(req, admin=True): return resposta
    try: banco.excluir(identificador)
    except ValueError as erro: return voltar('/', str(erro))
    return voltar('/', 'Produto arquivado')


@app.get('/movimentacoes')
def historico(req: Request):
    if resposta := checar(req): return resposta
    nome = req.query_params.get('nome', '')
    data = req.query_params.get('data', '')
    return tela(req, 'historico.html', registros=banco.historico(nome,data), nome=nome, data=data)


@app.get('/usuarios')
def usuarios(req: Request):
    if resposta := checar(req, admin=True): return resposta
    return tela(req, 'usuarios.html', usuarios=banco.pessoas())


@app.post('/usuarios')
async def novo_usuario(req: Request):
    if resposta := checar(req, admin=True): return resposta
    f = await req.form()
    try: banco.novo_usuario(str(f.get('login','')), str(f.get('senha','')), str(f.get('perfil','')))
    except ValueError as erro: return voltar('/usuarios', str(erro))
    return voltar('/usuarios', 'Usuário cadastrado')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=5000)
