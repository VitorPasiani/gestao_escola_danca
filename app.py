from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, jsonify
from operacoes import (
    cadastrar_aluno,  
    listar_alunos, 
    inativar_aluno, 
    buscar_aluno, 
    atualizar_aluno,
    listar_alunos_inativos,
    reativar_aluno,
    aluno_ja_tem_vinculo,
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
    listar_matriculas ,
    inativar_matricula,
    reativar_matricula,
    verificar_vinculo_turma,
    registrar_frequencia_particular,
    listar_inscricoes_particulares,
    buscar_valor_aula_por_inscricao,
    listar_ultimos_checkins,
    realizar_inscricao_aluno,
    listar_pendencias_particulares,
    faturar_aulas_selecionadas,
    listar_detalhes_inadimplencia,
    executar_limpeza_inadimplentes,
    gerar_relatorio_dre,
    consultar_saldos,
    registrar_saque,
    listar_historico_saques,
    quitar_taxa_matricula,
    cadastrar_despesa,
    clonar_despesas_mes_anterior,
    listar_despesas,
    quitar_despesa,
    excluir_despesa,
    atualizar_despesa
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

@app.route('/nova_matricula', methods=['GET', 'POST'])
def rota_nova_matricula():
    if request.method == 'POST':
        id_aluno = request.form.get('id_aluno')
        ids_turmas = request.form.getlist('id_turma') 
        status_form = request.form.get('status_matricula') 
        
        try:
            # --- TRAVA DE SEGURANÇA (VERIFICA CONFLITOS ANTES DE TUDO) ---
            for id_turma in ids_turmas:
                if not id_turma: continue
                
                status_existente = verificar_vinculo_turma(id_aluno, id_turma)
                
                if status_existente == 'Ativo':
                    flash("Conflito: O aluno já está ativamente matriculado em uma das turmas selecionadas!", "warning")
                    return redirect('/nova_matricula')
                elif status_existente == 'Inativo':
                    flash("Conflito: O aluno já possui matrícula trancada nesta turma. Acesse o Arquivo Morto (Matrículas Inativas) para reativá-la!", "danger")
                    return redirect('/nova_matricula')
            # -----------------------------------------------------------------

            ja_e_aluno = aluno_ja_tem_vinculo(id_aluno)
            pagou_taxa_nesta_sessao = False

            for id_turma in ids_turmas:
                if not id_turma: continue

                if ja_e_aluno:
                    status_final = 'Isento' 
                elif not pagou_taxa_nesta_sessao:
                    status_final = status_form 
                    pagou_taxa_nesta_sessao = True
                else:
                    status_final = 'Isento' 

                realizar_inscricao_aluno(id_aluno, id_turma, status_final)

            if ja_e_aluno:
                msg_vinculo = "Aluno já possuía vínculo ativo! Novas turmas adicionadas como Isentas de taxa."
            else:
                msg_vinculo = "Matrícula(s) realizada(s) com sucesso!"

            flash(msg_vinculo, "success")
            return redirect('/matriculas') 
            
        except Exception as e:
            flash(f"Erro ao processar matrícula: {str(e)}", "danger")
            return redirect('/nova_matricula')

    alunos = listar_alunos()
    turmas = listar_turmas()
    return render_template('cadastrar_matricula.html', lista_alunos=alunos, lista_turmas=turmas)

@app.route('/matriculas')
def pagina_listar_matriculas():
    matriculas = listar_matriculas(status_alvo='Ativo')
    return render_template('listar_matriculas.html', lista_de_matriculas=matriculas, inativos=False)

@app.route('/matriculas_inativas')
def pagina_listar_matriculas_inativas():
    matriculas = listar_matriculas(status_alvo='Inativo')
    return render_template('listar_matriculas.html', lista_de_matriculas=matriculas, inativos=True)

@app.route('/inativar_matricula/<int:id_inscricao>')
def rota_inativar_matricula(id_inscricao):
    mensagem = inativar_matricula(id_inscricao)
    flash(mensagem, "warning")
    return redirect('/matriculas')

@app.route('/reativar_matricula/<int:id_inscricao>')
def rota_reativar_matricula(id_inscricao):
    mensagem = reativar_matricula(id_inscricao)
    flash(mensagem, "success")
    return redirect('/matriculas')

@app.route('/quitar_taxa_matricula/<int:id_inscricao>', methods=['POST'])
def rota_quitar_taxa_matricula(id_inscricao):
    usar_maquininha = request.form.get('usar_maquininha') == '1'
    taxa_str = request.form.get('taxa_maquininha')

    taxa_decimal = 0.0
    if usar_maquininha and taxa_str:
        taxa_decimal = float(taxa_str) / 100.0

    try:
        mensagem = quitar_taxa_matricula(id_inscricao, usar_maquininha, taxa_decimal)
        flash(mensagem, 'success')
    except Exception as e:
        flash(f"Erro ao baixar taxa: {str(e)}", 'danger')

    return redirect('/matriculas')

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
        dias_semana_lista = request.form.getlist('dias_semana') if not is_particular else []
        sala = request.form.get('sala') if not is_particular else "Dinâmica"
        hora_inicio = request.form.get('hora_inicio') if not is_particular else ""
        hora_fim = request.form.get('hora_fim') if not is_particular else ""

        if not is_particular and sala != "Dinâmica":
            erro_conflito = verificar_conflito_sala(sala, dias_semana_lista, hora_inicio, hora_fim)
            if erro_conflito:
                flash(erro_conflito, "danger")
                return redirect('/cadastrar_turma')
        
        dados = {
            'nome_turma': request.form.get('nome_turma'),
            'id_professor': request.form.get('id_professor'),
            'sala': sala,
            'hora_inicio': hora_inicio,
            'hora_fim': hora_fim,
            'valor_base': request.form.get('valor_mensal_base'),
            'tipo_gestao': request.form.get('tipo_gestao') if not is_particular else "Parceiro",
            'dias_semana': dias_semana_lista,
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
        
        sala = request.form.get('sala') if not is_particular else "Dinâmica"
        dias_semana_lista = request.form.getlist('dias_semana') if not is_particular else []
        hora_inicio = request.form.get('hora_inicio') if not is_particular else ""
        hora_fim = request.form.get('hora_fim') if not is_particular else ""
        
        if not is_particular and sala != "Dinâmica":
            erro_conflito = verificar_conflito_sala(sala, dias_semana_lista, hora_inicio, hora_fim, id_turma_ignorada=id_turma)
            
            if erro_conflito:
                flash(erro_conflito, "danger")
                return redirect(f'/editar_turma/{id_turma}')

        dados_novos = {
            'nome_turma': request.form.get('nome_turma'),
            'id_professor': request.form.get('id_professor'),
            'sala': sala,
            'hora_inicio': hora_inicio,
            'hora_fim': hora_fim,
            'tipo_gestao': request.form.get('tipo_gestao') if not is_particular else "Parceiro",
            'is_particular': is_particular,
            'cronograma': request.form.get('cronograma_json') if is_particular else None,
            'valor_mensal_base': request.form.get('valor_mensal_base') if not is_particular else None,
            'valor_por_aula': request.form.get('valor_mensal_base') if is_particular else None 
        }

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
        
        # --- CAPTURANDO A LÓGICA DA MAQUININHA ---
        usar_maquininha = request.form.get('usar_maquininha') == '1'
        taxa_str = request.form.get('taxa_maquininha')
        
        taxa_decimal = 0.0
        if usar_maquininha and taxa_str:
            taxa_decimal = float(taxa_str) / 100.0 # Transforma 5.0% em 0.05
        # -----------------------------------------

        if tipo_gestao == 'Parceiro':
            percentual_repasse = 75.0
        else:
            percentual_repasse = 0.0

        try:
            # Passando a taxa_decimal como último parâmetro
            mensagem = cadastrar_aula_avulsa(aluno_nome, nome_professor, data_aula, valor_total, percentual_repasse, taxa_decimal)
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
        
        if not id_inscricao:
            flash("Atenção: Por favor, selecione um aluno válido na lista para registrar a presença.", "warning")
            return redirect('/checkin_particular')
        
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

@app.route('/faturamento_particulares', methods=['GET', 'POST'])
def rota_faturamento_particulares():
    if request.method == 'POST':
        aulas_selecionadas = request.form.getlist('aulas_selecionadas')
        
        usar_maquininha = request.form.get('usar_maquininha') == '1'
        taxa_str = request.form.get('taxa_maquininha')
        
        taxa_decimal = 0.0
        if usar_maquininha and taxa_str:
            taxa_decimal = float(taxa_str) / 100.0
        
        if not aulas_selecionadas:
            flash("Por favor marque as aulas para faturamento!", "warning")
        else:
            mensagem = faturar_aulas_selecionadas(aulas_selecionadas, taxa_decimal)
            flash(mensagem, "success")
            
        return redirect('/faturamento_particulares')

    pendencias = listar_pendencias_particulares()
    return render_template('faturamento_particulares.html', alunos_pendentes=pendencias)

### RELATÓRIOS E LIMPEZAS INADIMPLENTES ###
@app.route('/painel_inadimplencia', methods=['GET', 'POST'])
def rota_painel_inadimplencia():
    if request.method == 'POST':
        mensagem = executar_limpeza_inadimplentes()
        flash(mensagem, "danger")
        return redirect('/painel_inadimplencia')

    lista = listar_detalhes_inadimplencia()
    return render_template('painel_inadimplencia.html', inadimplentes=lista)

@app.route('/dre_mensal', methods=['GET', 'POST'])
def rota_dre_mensal():
    relatorio = None
    
    if request.method == 'POST':
        mes_referencia = request.form.get('mes_referencia')
        despesas_fixas = float(request.form.get('despesas_fixas') or 0.0)
        retencao_caixa = float(request.form.get('retencao_caixa') or 0.0)
        
        relatorio = gerar_relatorio_dre(mes_referencia, despesas_fixas, retencao_caixa)
        
    return render_template('dre_mensal.html', relatorio=relatorio)

##### FINANCEIRO - SAQUES E SALDOS #####
@app.route('/gestao_caixas', methods=['GET', 'POST'])
def rota_gestao_caixas():
    if request.method == 'POST':
        caixa_origem = request.form.get('caixa_origem')
        descricao = request.form.get('descricao')
        valor = float(request.form.get('valor'))
        
        mensagem, categoria = registrar_saque(caixa_origem, descricao, valor)
        flash(mensagem, categoria)
        return redirect('/gestao_caixas')
        
    saldos_atuais = consultar_saldos()
    historico = listar_historico_saques()
    
    return render_template('gestao_caixas.html', saldos=saldos_atuais, historico=historico)

### DESPESAS FIXAS E VARIÁVEIS ###
@app.route('/despesas', methods=['GET', 'POST'])
def pagina_despesas():
    if request.method == 'POST':
        descricao = request.form.get('descricao')
        tipo = request.form.get('tipo_despesa')
        valor = float(request.form.get('valor') or 0.0)
        vencimento = request.form.get('data_vencimento')
        mes_ref = request.form.get('mes_referencia')

        mensagem = cadastrar_despesa(descricao, tipo, valor, vencimento, mes_ref)
        flash(mensagem, 'success')
        return redirect(f'/despesas?mes={mes_ref}')

    mes_atual = request.args.get('mes')
    if not mes_atual:
        mes_atual = datetime.now().strftime("%m/%Y")

    lista = listar_despesas(mes_atual)
    return render_template('gestao_despesas.html', lista_despesas=lista, mes_atual=mes_atual)

@app.route('/clonar_despesas', methods=['POST'])
def rota_clonar_despesas():
    mes_novo = request.form.get('mes_novo')
    mes_anterior = request.form.get('mes_anterior')
    
    mensagem = clonar_despesas_mes_anterior(mes_novo, mes_anterior)
    flash(mensagem, 'info')
    return redirect(f'/despesas?mes={mes_novo}')

@app.route('/quitar_despesa/<int:id_despesa>')
def rota_quitar_despesa(id_despesa):
    mensagem = quitar_despesa(id_despesa)
    flash(mensagem, 'success')
    return redirect(request.referrer or '/despesas')

@app.route('/editar_despesa/<int:id_despesa>', methods=['POST'])
def rota_editar_despesa(id_despesa):
    descricao = request.form.get('descricao')
    tipo = request.form.get('tipo_despesa')
    valor = float(request.form.get('valor') or 0.0)
    vencimento = request.form.get('data_vencimento')
    mes_ref = request.form.get('mes_referencia')

    mensagem = atualizar_despesa(id_despesa, descricao, tipo, valor, vencimento, mes_ref)
    flash(mensagem, 'success')
    return redirect(request.referrer or f'/despesas?mes={mes_ref}')

@app.route('/excluir_despesa/<int:id_despesa>')
def rota_excluir_despesa(id_despesa):
    mensagem = excluir_despesa(id_despesa)
    flash(mensagem, 'warning')
    return redirect(request.referrer or '/despesas')

## MAIN ##
if __name__ == '__main__':
    app.run(debug=True)