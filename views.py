from flask import render_template, request, redirect, session, flash, url_for, send_from_directory
from models import Jogo, Usuario
from dao import JogoDao, UsuarioDao

import os
import time

from jogoteca import db, app
from helpers import deleta_arquivo, recupera_imagem

jogodao = JogoDao(db)
usuariodao = UsuarioDao(db)


@app.route('/')
def index():
    lista = jogodao.listar()
    return render_template('lista.html',titulo='Jogos', jogos=lista)

@app.route('/novo')
def novo():
    if ('usuario_logado' not in session )or (session['usuario_logado'] == None):
        return redirect(url_for('login',proxima= url_for('novo')))
    return render_template('novo.html',titulo='Novo Jogo')


@app.route('/criar', methods=['POST',])
def criar():
    nome = request.form['nome']
    categoria = request.form['categoria']
    console = request.form['console']

    jogo = Jogo(nome,categoria,console)
    
    jogo = jogodao.salvar(jogo)

    arquivo = request.files['arquivo']
    upload_path = app.config['UPLOAD_PATH']

    timestamp = time.time()

    arquivo.save(f'{upload_path}/capa{jogo.id}-{timestamp}.jpg')

    return redirect(url_for('index'))

@app.route('/editar/<int:id>')
def editar(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('editar')))
    jogo = jogodao.busca_por_id(id)
    nome_imagem =  recupera_imagem(id)
    capa_jogo = f'capa{id}.jpg'
    return render_template('editar.html', titulo='Editando jogo', jogo=jogo, capa_jogo = nome_imagem)


@app.route('/atualizar', methods=['POST',])
def atualizar():
    nome = request.form['nome']
    categoria = request.form['categoria']
    console = request.form['console']
    jogo = Jogo(nome, categoria, console, id=request.form['id'])
    jogodao.salvar(jogo)

    arquivo = request.files['arquivo']
    upload_path = app.config['UPLOAD_PATH']
    timestamp = time.time()
    deleta_arquivo(jogo.id)
    arquivo.save(f'{upload_path}/capa{jogo.id}-{timestamp}.jpg')
    return redirect(url_for('index'))

@app.route('/deletar/<int:id>')
def deletar(id):
    jogodao.deletar(id)
    flash('O jogo foi Removido com sucesso!')
    return redirect(url_for('index'))



@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)

@app.route('/autenticar', methods=['POST',])
def autenticar():
    usuario = usuariodao.buscar_por_id(request.form['usuario'])
    if usuario:
            if usuario.senha == request.form['senha']:
                session['usuario_logado'] = usuario.id
                flash(usuario.nome + ' logou com sucesso!')
                proxima_pagina = request.form['proxima']
                return redirect(proxima_pagina)
    else:
        flash(request.form['usuario'] + ' Nao logado, tente novamente!')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Nenhum usuario logado!')
    return redirect(url_for('index'))

@app.route('/uploads/<nome_arquivo>')
def imagem(nome_arquivo):
    return send_from_directory('uploads',nome_arquivo)