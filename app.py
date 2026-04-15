from flask import Flask, render_template, request, redirect, flash, jsonify
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
    listar_turmas_inativas,
    atualizar_turma,
    inativar_turma,
    deletar_turma_definitivo,
    buscar_turma,
    verificar_conflito_sala,
    cadastrar_plano,
    atualizar_plano,
    listar_planos,
    inativar_plano,
    buscar_plano,
    deletar_plano_definitivo,
    listar_planos_inativos,
    cadastrar_aula_avulsa,
    listar_aulas_avulsas,
    deletar_aula_avulsa,
    registrar_frequencia_particular,
    listar_inscricoes_particulares,
    buscar_valor_aula_por_inscricao,
    listar_ultimos_checkins
)

import sqlite3
import json

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
        
        except ValueError as e:
            flash(str(e), "danger")
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
    return render_template('listar_alunos.html', lista_de_alunos=lista_banco, inativos=True)

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
        
    return render_template('cadastrar_aluno.html', aluno=aluno_encontrado, editando=True)

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
        
    return render_template('cadastrar_professor.html', professor=professor_encontrado, editando=True)

### TURMAS ###
@app.route('/cadastrar_turma', methods=['GET', 'POST'])
def rota_cadastrar_turma():
    if request.method == 'POST':
        is_particular = request.form.get('is_particular') == '1'
        
        dados = {
            'nome_turma': request.form.get('nome_turma'),
            'id_professor': request.form.get('id_professor'),
            'sala': request.form.get('sala') if not is_particular else "Dinâmica",
            'hora_inicio': request.form.get('hora_inicio') if not is_particular else "",
            'hora_fim': request.form.get('hora_fim') if not is_particular else "",
            'valor_base': request.form.get('valor_mensal_base'),
            'tipo_gestao': request.form.get('tipo_gestao') if not is_particular else "Parceiro",
            'dias_semana': request.form.getlist('dias_semana') if not is_particular else [],
            'cronograma': request.form.get('cronograma_json') if is_particular else None
        }

        dias_semana_texto = ", ".join(dados['dias_semana']) if not is_particular else None
        valor_mensal = dados['valor_base'] if not is_particular else None
        valor_aula = dados['valor_base'] if is_particular else None

        mensagem = cadastrar_turma(
            nome_turma=dados['nome_turma'], 
            tipo_gestao=dados['tipo_gestao'], 
            sala=dados['sala'], 
            id_professor=dados['id_professor'], 
            hora_inicio=dados['hora_inicio'], 
            hora_fim=dados['hora_fim'], 
            dias_semana=dias_semana_texto, 
            valor_mensal_base=valor_mensal,
            is_particular=is_particular,
            cronograma=dados['cronograma'],
            valor_por_aula=valor_aula
        )
        
        flash(mensagem, 'success')
        return redirect('/turmas')

    professores_ativos = listar_professores()
    return render_template('cadastrar_turma.html', lista_professores=professores_ativos, valores_antigos={})

@app.route('/turmas')
def pagina_listar_turmas():
    turmas_banco = listar_turmas()
    return render_template('listar_turmas.html', lista_de_turmas=turmas_banco)

@app.route('/deletar_turma/<int:id_turma>')
def rota_deletar_turma(id_turma):
    mensagem = inativar_turma(id_turma)
    flash(mensagem, 'success')
    return redirect('/turmas')

@app.route('/editar_turma/<int:id_turma>', methods=['GET', 'POST'])
def rota_editar_turma(id_turma):
    if request.method == 'POST':
        is_particular = request.form.get('is_particular') == '1'
        
        dados_novos = {
            'nome_turma': request.form.get('nome_turma'),
            'id_professor': request.form.get('id_professor'),
            'sala': request.form.get('sala') if not is_particular else "Dinâmica",
            'hora_inicio': request.form.get('hora_inicio') if not is_particular else "",
            'hora_fim': request.form.get('hora_fim') if not is_particular else "",
            'tipo_gestao': request.form.get('tipo_gestao') if not is_particular else "Parceiro",
            'is_particular': is_particular,
            'cronograma': request.form.get('cronograma_json') if is_particular else None,
            'valor_mensal_base': request.form.get('valor_mensal_base') if not is_particular else None,
            'valor_por_aula': request.form.get('valor_mensal_base') if is_particular else None 
        }

        dias_semana_lista = request.form.getlist('dias_semana') if not is_particular else []
        dados_novos['dias_semana'] = ", ".join(dias_semana_lista) if not is_particular else None

        mensagem = atualizar_turma(id_turma, **dados_novos)
        flash(mensagem, 'success')
        return redirect('/turmas')

    turma_existente = buscar_turma(id_turma)
    if not turma_existente:
        flash("Turma não encontrada!", "danger")
        return redirect('/turmas')
    
    if turma_existente.get('dias_semana'):
        turma_existente['dias_semana'] = turma_existente['dias_semana'].split(', ')
    
    professores = listar_professores()
    return render_template('cadastrar_turma.html', 
                           lista_professores=professores, 
                           valores_antigos=turma_existente,
                           editando=True,
                           id_turma=id_turma)

@app.route('/turmas_inativas')
def pagina_turmas_inativas():
    turmas_banco = listar_turmas_inativas()
    return render_template('listar_turmas.html', lista_de_turmas=turmas_banco, inativas=True)

@app.route('/excluir_turma/<int:id_turma>')
def rota_excluir_turma(id_turma):
    mensagem, categoria = deletar_turma_definitivo(id_turma)
    flash(mensagem, categoria)
    return redirect('/turmas_inativas')

### PLANOS ###
@app.route('/cadastrar_plano', methods=['GET', 'POST'])
def pagina_cadastrar_plano():
    if request.method == 'POST':
        nome_plano = request.form.get('nome_plano')
        percentual_desconto = request.form.get('percentual_desconto')
        duracao_meses = request.form.get('duracao_meses')

        mensagem = cadastrar_plano(nome_plano, percentual_desconto, duracao_meses)
        flash(mensagem, 'success')
        return redirect('/planos')

    return render_template('cadastrar_plano.html', valores_antigos={})

@app.route('/planos')
def pagina_listar_planos():
    planos_banco = listar_planos()
    return render_template('listar_planos.html', lista_de_planos=planos_banco)

@app.route('/excluir_plano/<int:id_plano>')
def rota_excluir_plano(id_plano):
    mensagem, categoria = deletar_plano_definitivo(id_plano)
    flash(mensagem, categoria)
    return redirect('/planos_inativos')

@app.route('/inativar_plano/<int:id_plano>')
def rota_inativar_plano(id_plano):
    mensagem = inativar_plano(id_plano)
    flash(mensagem, 'success')
    return redirect('/planos')

@app.route('/planos_inativos')
def pagina_planos_inativos():
    planos_banco = listar_planos_inativos()
    return render_template('listar_planos.html', lista_de_planos=planos_banco, inativos=True)

@app.route('/editar_plano/<int:id_plano>', methods=['GET', 'POST'])
def rota_editar_plano(id_plano):
    if request.method == 'POST':
        dados_novos = {
            "nome_plano": request.form.get('nome_plano'),
            "percentual_desconto": request.form.get('percentual_desconto'),
            "duracao_meses": request.form.get('duracao_meses')
        }
        
        mensagem = atualizar_plano(id_plano, **dados_novos)
        flash(mensagem, 'success')
        return redirect('/planos')

    plano_encontrado = buscar_plano(id_plano)
    if not plano_encontrado:
        flash("Plano não encontrado!", "danger")
        return redirect('/planos')
        
    return render_template('cadastrar_plano.html', valores_antigos=plano_encontrado, editando=True, id_plano=id_plano)

### CRONOGRAMA DE SALAS ##
@app.route('/cronograma')
def pagina_cronograma():
    return render_template('cronograma.html')


@app.route('/api/cronograma')
def api_cronograma():
    turmas_ativas = listar_turmas()
    eventos = []
    mapa_dias = {'Domingo': 0, 'Segunda': 1, 'Terça': 2, 'Quarta': 3, 'Quinta': 4, 'Sexta': 5, 'Sábado': 6}

    for t in turmas_ativas:
        # LÓGICA 1: TURMA PARTICULAR
        if t['is_particular'] and t['cronograma']:
            cor_evento = "#203760" 
            grade = json.loads(t['cronograma'])
            
            for aula in grade:
                eventos.append({
                    "title": f"{t['nome_turma']} | {aula['sala']} ({t['nome_professor']})",
                    "daysOfWeek": [mapa_dias[aula['dia']]],
                    "startTime": aula['inicio'],
                    "endTime": aula['fim'],
                    "color": cor_evento
                })
                
        # LÓGICA 2: TURMA REGULAR
        elif t['dias_semana'] and t['dias_semana'] != "Grade Dinâmica":
            dias_lista = t['dias_semana'].split(', ')
            dias_numeros = [mapa_dias[dia] for dia in dias_lista if dia in mapa_dias]
            cor_evento = "#0dcaf0" if t['sala'] == 'Sala Pequena' else "#f5c5d1"
            hora_inicio, hora_fim = t['horario'].split(' às ')

            eventos.append({
                "title": f"{t['nome_turma']} | {t['sala']} ({t['nome_professor']})",
                "daysOfWeek": dias_numeros,
                "startTime": hora_inicio,
                "endTime": hora_fim,
                "color": cor_evento
            })
            
    return jsonify(eventos)

### AULAS AVULSAS/PARTICULARES ###
@app.route('/registrar_avulsa', methods=['GET', 'POST'])
def rota_registrar_avulsa():
    if request.method == 'POST':
        aluno_nome = request.form.get('aluno_nome')
        nome_professor = request.form.get('nome_professor')
        data_aula = request.form.get('data_aula')
        valor_total = float(request.form.get('valor_total'))
        
        tipo_gestao = request.form.get('tipo_gestao')
        
        if tipo_gestao == 'Parceiro':
            percentual_repasse = 75.0
        else:
            percentual_repasse = 0.0

        try:
            mensagem = cadastrar_aula_avulsa(aluno_nome, nome_professor, data_aula, valor_total, percentual_repasse)
            flash(mensagem, 'success')
            return redirect('/aulas_avulsas')
        except Exception as e:
            flash(f"Erro ao registrar aula: {str(e)}", "danger")
            return redirect('/registrar_avulsa')

    professores = listar_professores()
    return render_template('cadastrar_aula_avulsa.html', lista_professores=professores)

@app.route('/aulas_avulsas')
def pagina_listar_avulsas():
    aulas = listar_aulas_avulsas()
    return render_template('listar_aulas_avulsas.html', lista_de_aulas=aulas)

@app.route('/excluir_avulsa/<int:id_aula>')
def rota_excluir_avulsa(id_aula):
    mensagem = deletar_aula_avulsa(id_aula)
    flash(mensagem, 'success')
    return redirect('/aulas_avulsas')

### FREQUÊNCIA / CHECK-IN (AULAS PARTICULARES) ###
@app.route('/checkin_particular', methods=['GET', 'POST'])
def rota_checkin_particular():
    if request.method == 'POST':
        id_inscricao = request.form.get('id_inscricao')
        data_aula = request.form.get('data_aula')
        
        valor_aula = buscar_valor_aula_por_inscricao(id_inscricao)
        
        try:
            mensagem = registrar_frequencia_particular(id_inscricao, data_aula, valor_aula)
            flash(mensagem, 'success')
            return redirect('/checkin_particular')
        except Exception as e:
            flash(f"Erro: {str(e)}", "danger")
            return redirect('/checkin_particular')

    inscricoes = listar_inscricoes_particulares()
    historico = listar_ultimos_checkins()

    return render_template('checkin_particular.html', 
                           lista_inscricoes=inscricoes,
                           lista_historico=historico)

## MAIN ##
if __name__ == '__main__':
    app.run(debug=True)