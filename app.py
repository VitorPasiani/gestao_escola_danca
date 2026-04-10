from flask import Flask, render_template, request, redirect, flash
from operacoes import (
    cadastrar_aluno,  
    listar_alunos, 
    inativar_aluno, 
    buscar_aluno, 
    atualizar_aluno,
    listar_alunos_inativos,
    reativar_aluno,
    cadastrar_professor,
    listar_professores,
    deletar_professor,
    buscar_professor,
    atualizar_professor,
    cadastrar_turma,
    listar_turmas,
    verificar_conflito_sala
)

import sqlite3

app = Flask(__name__)
app.secret_key = 'chave_secreta_espaco_ato'

@app.route('/')
def pagina_inicial():
    escola = "Espaço de Dança ATO"
    turmas_ativas = listar_turmas()
    return render_template('index.html', nome_dinamico=escola, lista_de_turmas=turmas_ativas)

### ALUNOS ###
@app.route('/cadastrar_aluno', methods=['GET', 'POST'])
def pagina_cadastrar_aluno():
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        rg = request.form.get('rg')
        endereco = request.form.get('endereco')
        data_nascimento = request.form.get('data_nascimento')
        email = request.form.get('email')
        contato_1 = request.form.get('contato_1')
        contato_2 = request.form.get('contato_2')
        responsavel = request.form.get('responsavel')

        try:
            cadastrar_aluno(nome, cpf, rg, endereco, data_nascimento, email, contato_1, contato_2, responsavel)
            flash('Aluno cadastrado com sucesso!', 'success')
            return redirect('/cadastrar_aluno')
        
        except sqlite3.IntegrityError:
            flash("Atenção: Já existe um aluno cadastrado com esse CPF!", "danger")
            return redirect('/cadastrar_aluno')

    return render_template('cadastrar_aluno.html')

@app.route('/alunos')
def pagina_listar_alunos():
    alunos_banco = listar_alunos()

    return render_template('listar_alunos.html', lista_de_alunos=alunos_banco)

@app.route('/inativar_aluno/<int:id_aluno>')
def rota_inativar_aluno(id_aluno):
    mensagem_retorno = inativar_aluno(id_aluno)
    
    flash(mensagem_retorno, 'success')
    
    return redirect('/alunos')

@app.route('/alunos_inativos')
def pagina_alunos_inativos():
    lista_banco = listar_alunos_inativos()
    return render_template('listar_alunos_inativos.html', lista_de_alunos=lista_banco)

@app.route('/reativar_aluno/<int:id_aluno>')
def rota_reativar_aluno(id_aluno):
    mensagem_retorno = reativar_aluno(id_aluno)

    flash(mensagem_retorno, 'success')
    
    return redirect('/alunos_inativos')


@app.route('/editar_aluno/<int:id_aluno>', methods=['GET', 'POST'])
def rota_editar_aluno(id_aluno):

    rg_recebido = request.form.get('rg', '').strip()
    rg_tratado = None if rg_recebido == "" else rg_recebido

    if request.method == 'POST':
        dados_novos = {
            "nome": request.form.get('nome'),
            "cpf": request.form.get('cpf'),
            "rg": rg_tratado,
            "endereco": request.form.get('endereco'),
            "data_nascimento": request.form.get('data_nascimento'),
            "email": request.form.get('email'),
            "contato_1": request.form.get('contato_1'),
            "contato_2": request.form.get('contato_2'),
            "responsavel": request.form.get('responsavel')
        }

        mensagem = atualizar_aluno(id_aluno, **dados_novos)
        
        flash(mensagem, 'success')
        return redirect('/alunos')

    aluno_encontrado = buscar_aluno(id_aluno)
    
    if not aluno_encontrado:
        flash("Aluno não encontrado!", "danger")
        return redirect('/alunos')
        
    return render_template('editar_aluno.html', aluno=aluno_encontrado)


### PROFESSORES ###
@app.route('/cadastrar_professor', methods=['GET', 'POST'])
def pagina_cadastrar_professor():
    if request.method == 'POST':
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        chave_pix = request.form.get('chave_pix')

        cadastrar_professor(nome, telefone, chave_pix)
        flash('Professor cadastrado com sucesso!', 'success')

        return redirect('/cadastrar_professor')

    return render_template('cadastrar_professor.html')     

@app.route('/professores')
def pagina_listar_professores():
    professores_banco = listar_professores()

    return render_template('listar_professores.html', lista_de_professores=professores_banco)

@app.route('/deletar_professor/<int:id_professor>')
def rota_deletar_professor(id_professor):
    mensagem = deletar_professor(id_professor)
    flash(mensagem, 'success')
    return redirect('/professores')

@app.route('/editar_professor/<int:id_professor>', methods=['GET', 'POST'])
def rota_editar_professor(id_professor):
    if request.method == 'POST':
        dados_novos = {
            "nome": request.form.get('nome'),
            "telefone": request.form.get('telefone'),
            "chave_pix": request.form.get('chave_pix')
        }
        
        mensagem = atualizar_professor(id_professor, **dados_novos)
        flash(mensagem, 'success')
        return redirect('/professores')

    professor_encontrado = buscar_professor(id_professor)
    
    if not professor_encontrado:
        flash("Professor não encontrado!", "danger")
        return redirect('/professores')
        
    return render_template('editar_professor.html', professor=professor_encontrado)

## TURMAS ##
@app.route('/cadastrar_turma', methods=['GET', 'POST'])
def rota_cadastrar_turma():
    if request.method == 'POST':
        dados = {
            'nome_turma': request.form.get('nome_turma'),
            'id_professor': request.form.get('id_professor'),
            'sala': request.form.get('sala'),
            'hora_inicio': request.form.get('hora_inicio'),
            'hora_fim': request.form.get('hora_fim'),
            'valor_mensal_base': request.form.get('valor_mensal_base'),
            'tipo_gestao': request.form.get('tipo_gestao'),
            'dias_semana': request.form.getlist('dias_semana')
        }

        conflito = verificar_conflito_sala(dados['sala'], dados['dias_semana'], dados['hora_inicio'], dados['hora_fim'])
        
        if conflito:
            flash(conflito, 'danger')
            professores_ativos = listar_professores()
            return render_template('cadastrar_turma.html', 
                                 lista_professores=professores_ativos, 
                                 valores_antigos=dados)

        dias_semana_texto = ", ".join(dados['dias_semana'])
        mensagem = cadastrar_turma(
            dados['nome_turma'], dados['tipo_gestao'], dados['sala'], 
            dados['id_professor'], dados['hora_inicio'], dados['hora_fim'], 
            dias_semana_texto, dados['valor_mensal_base']
        )
        
        flash(mensagem, 'success')
        return redirect('/turmas')

    professores_ativos = listar_professores()
    return render_template('cadastrar_turma.html', lista_professores=professores_ativos, valores_antigos={})

@app.route('/turmas')
def pagina_listar_turmas():
    turmas_banco = listar_turmas()
    return render_template('listar_turmas.html', lista_de_turmas=turmas_banco)

if __name__ == '__main__':
    app.run(debug=True)