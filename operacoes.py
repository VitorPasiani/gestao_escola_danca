import sqlite3
import calendar
from datetime import datetime

##### UTILS #####

def conectar_banco():
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()
    cursor.execute('PRAGMA foreign_keys = ON;')
    return conexao, cursor

def adicionar_meses(data_original, meses_para_adicionar): 
    mes = data_original.month - 1 + meses_para_adicionar
    ano = data_original.year + mes // 12
    mes = mes % 12 + 1
    dia = min(data_original.day, calendar.monthrange(ano, mes)[1])
    
    return data_original.replace(year=ano, month=mes, day=dia)


###### ALUNOS ######
def cadastrar_aluno(nome, cpf=None, rg=None, endereco=None, data_nascimento=None, email=None, contato_1=None, contato_2=None, responsavel=None):
    conexao, cursor = conectar_banco()
    
    sql = '''
        INSERT INTO alunos (nome, cpf, rg, endereco, data_nascimento, email, contato_1, contato_2, responsavel)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    valores = (nome, cpf, rg, endereco, data_nascimento, email, contato_1, contato_2, responsavel)

    cursor.execute(sql, valores)
    conexao.commit()
    conexao.close()

    return f"Aluno(a) {nome} cadastrado(a) com sucesso!"

def atualizar_aluno(id_aluno, **kwargs):
    if not kwargs:
        return "Nenhuma informação enviada para atualização."
    
    conexao, cursor = conectar_banco()

    campos_sql = [] 
    valores = [] 

    for coluna, novo_valor in kwargs.items():
        campos_sql.append(f"{coluna} = ?") 
        valores.append(novo_valor) 

    texto_set = ", ".join(campos_sql) 

    sql = f'''
        UPDATE alunos
        SET {texto_set}
        WHERE id_aluno = ?
    '''
    valores.append(id_aluno) 

    cursor.execute(sql, tuple(valores)) 
    conexao.commit()
    conexao.close()

    return f"Cadastro atualizado com sucesso!"

def listar_alunos():
    conexao, cursor = conectar_banco()

    cursor.execute('SELECT id_aluno, nome, cpf, contato_1 FROM alunos WHERE ativo = 1')
    alunos_banco = cursor.fetchall()
    conexao.close()

    lista_alunos = []
    for a in alunos_banco:
        lista_alunos.append({
            "id_aluno": a[0],
            "nome": a[1],
            "cpf": a[2],
            "contato": a[3]
        })
            
    return lista_alunos

def listar_alunos_inativos():
    conexao, cursor = conectar_banco()

    cursor.execute('SELECT id_aluno, nome, cpf, contato_1 FROM alunos WHERE ativo = 0')
    alunos_banco = cursor.fetchall()
    conexao.close()

    lista_inativos = []
    for a in alunos_banco:
        lista_inativos.append({
            "id_aluno": a[0],
            "nome": a[1],
            "cpf": a[2],
            "contato": a[3]
        })
            
    return lista_inativos

def deletar_aluno(id_aluno):
    conexao, cursor = conectar_banco()

    sql = '''
        UPDATE alunos
        SET ativo = 0
        WHERE id_aluno = ?
    '''
    cursor.execute(sql, (id_aluno,))
    conexao.commit()
    conexao.close()

    return "Matrícula inativada com sucesso! Histórico financeiro mantido."

def reativar_aluno(id_aluno):
    conexao, cursor = conectar_banco()

    cursor.execute('SELECT nome FROM alunos WHERE id_aluno = ?', (id_aluno,))
    resultado = cursor.fetchone()

    if resultado:
        nome_aluno = resultado[0]
        
        sql = '''
            UPDATE alunos
            SET ativo = 1
            WHERE id_aluno = ?
        '''
        cursor.execute(sql, (id_aluno,))
        conexao.commit()
        mensagem = f"Matrícula de {nome_aluno} reativada com sucesso!"
    else:
        mensagem = "Ops! Não encontrei nenhum aluno com esse registro para reativar."

    conexao.close()
    return mensagem


###### PROFESSORES ######
def cadastrar_professor(nome, telefone=None, chave_pix=None):
    conexao, cursor = conectar_banco()

    sql = '''
        INSERT INTO professores (nome, telefone, chave_pix)
        VALUES (?, ?, ?)
    '''
    cursor.execute(sql, (nome, telefone, chave_pix))
    conexao.commit()
    conexao.close()

    return f"Professor(a) {nome} cadastrado(a) com sucesso!"

def atualizar_professor(id_professor, **kwargs):
    if not kwargs:
        return "Nenhuma informação a ser atualizada."
    
    conexao, cursor = conectar_banco()
    campos_sql = []
    valores = []

    for coluna, novo_valor in kwargs.items():
        campos_sql.append(f"{coluna} = ?")
        valores.append(novo_valor)

    texto_set = ", ".join(campos_sql)
    sql = f'UPDATE professores SET {texto_set} WHERE id_professor = ?'
    valores.append(id_professor)

    cursor.execute(sql, tuple(valores))
    conexao.commit()
    conexao.close()

    return "Cadastro do professor atualizado com sucesso!"

def listar_professores():
    conexao, cursor = conectar_banco()

    cursor.execute('SELECT id_professor, nome, telefone, chave_pix FROM professores WHERE ativo = 1')
    profs_banco = cursor.fetchall()
    conexao.close()

    lista_professores = []
    for p in profs_banco:
        lista_professores.append({
            "id_professor": p[0],
            "nome": p[1],
            "telefone": p[2],
            "chave_pix": p[3]
        })
            
    return lista_professores

def deletar_professor(id_professor):
    conexao, cursor = conectar_banco()

    sql = 'UPDATE professores SET ativo = 0 WHERE id_professor = ?'
    cursor.execute(sql, (id_professor,))
    conexao.commit()
    conexao.close()

    return "Cadastro do professor foi inativado no sistema!"


###### PLANOS ######
def cadastrar_plano(nome_plano, percentual_desconto, duracao_meses=1):
    conexao, cursor = conectar_banco()

    sql = '''
        INSERT INTO planos (nome_plano, percentual_desconto, duracao_meses)
        VALUES (?, ?, ?)
    '''
    cursor.execute(sql, (nome_plano, percentual_desconto, duracao_meses))
    conexao.commit()
    conexao.close()

    return f"Plano '{nome_plano}' cadastrado com sucesso!"

def atualizar_plano(id_plano, **kwargs):
    if not kwargs:
        return "Nenhuma informação a ser atualizada."
    
    conexao, cursor = conectar_banco()
    campos_sql = []
    valores = []

    for coluna, novo_valor in kwargs.items():
        campos_sql.append(f"{coluna} = ?")
        valores.append(novo_valor)

    texto_set = ", ".join(campos_sql)
    sql = f'UPDATE planos SET {texto_set} WHERE id_plano = ?'
    valores.append(id_plano)

    cursor.execute(sql, tuple(valores))
    conexao.commit()
    conexao.close()

    return "Plano atualizado com sucesso!"

def listar_planos():
    conexao, cursor = conectar_banco()

    cursor.execute('SELECT id_plano, nome_plano, percentual_desconto, duracao_meses FROM planos')
    planos_banco = cursor.fetchall()
    conexao.close()

    lista_planos = []
    for p in planos_banco:
        lista_planos.append({
            "id_plano": p[0],
            "nome_plano": p[1],
            "percentual_desconto": p[2],
            "duracao_meses": p[3]
        })
            
    return lista_planos

def deletar_plano(id_plano):
    conexao, cursor = conectar_banco()

    sql = 'DELETE FROM planos WHERE id_plano = ?'
    cursor.execute(sql, (id_plano,))
    conexao.commit()
    conexao.close()

    return "Plano excluído do sistema!"


###### TURMAS ######
def cadastrar_turma(nome_turma, tipo_gestao, id_professor=None, horario=None, dias_semana=None, valor_mensal_base=None, is_particular=False, cronograma=None, valor_por_aula=None):
    conexao, cursor = conectar_banco()

    sql = '''
        INSERT INTO turmas (nome_turma, id_professor, horario, dias_semana, valor_mensal_base, tipo_gestao, is_particular, cronograma, valor_por_aula)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    valores = (nome_turma, id_professor, horario, dias_semana, valor_mensal_base, tipo_gestao, is_particular, cronograma, valor_por_aula)

    cursor.execute(sql, valores)
    conexao.commit()
    conexao.close()

    return f"Turma '{nome_turma}' cadastrada com sucesso!"

def atualizar_turma(id_turma, **kwargs):
    if not kwargs:
        return "Nenhuma informação a ser atualizada."
    
    conexao, cursor = conectar_banco()
    campos_sql = []
    valores = []

    for coluna, novo_valor in kwargs.items():
        campos_sql.append(f"{coluna} = ?")
        valores.append(novo_valor)

    texto_set = ", ".join(campos_sql)
    sql = f'UPDATE turmas SET {texto_set} WHERE id_turma = ?'
    valores.append(id_turma)

    cursor.execute(sql, tuple(valores))
    conexao.commit()
    conexao.close()

    return "Dados da turma atualizados com sucesso!"

def listar_turmas():
    conexao, cursor = conectar_banco()

    sql = '''
        SELECT
            turmas.id_turma,
            turmas.nome_turma,
            professores.nome,
            turmas.horario,
            turmas.dias_semana,
            turmas.valor_mensal_base
        FROM turmas
        LEFT JOIN professores ON turmas.id_professor = professores.id_professor
        WHERE turmas.ativo = 1
    '''
    cursor.execute(sql)
    turmas_banco = cursor.fetchall()
    conexao.close()

    lista_turmas = []
    for t in turmas_banco:
        lista_turmas.append({
            "id_turma": t[0],
            "nome_turma": t[1],
            "nome_professor": t[2] if t[2] else "Sem Professor",
            "horario": t[3],
            "dias_semana": t[4],
            "valor_mensal_base": t[5]
        })
        
    return lista_turmas

def deletar_turma(id_turma):
    conexao, cursor = conectar_banco()

    sql = 'UPDATE turmas SET ativo = 0 WHERE id_turma = ?'
    cursor.execute(sql, (id_turma,))
    conexao.commit()
    conexao.close()

    return "Turma inativada no sistema!"


##### EVENTOS ######
def cadastrar_evento(nome_evento, data_evento=None):
    conexao, cursor = conectar_banco()

    sql = 'INSERT INTO eventos (nome_evento, data_evento) VALUES (?, ?)'
    cursor.execute(sql, (nome_evento, data_evento))
    conexao.commit()
    conexao.close()

    return f"Evento '{nome_evento}' agendado com sucesso!"

def atualizar_evento(id_evento, **kwargs):
    if not kwargs:
        return "Nenhuma informação a ser atualizada."
    
    conexao, cursor = conectar_banco()
    campos_sql = []
    valores = []

    for coluna, novo_valor in kwargs.items():
        campos_sql.append(f"{coluna} = ?")
        valores.append(novo_valor)

    texto_set = ", ".join(campos_sql)
    sql = f'UPDATE eventos SET {texto_set} WHERE id_evento = ?'
    valores.append(id_evento)

    cursor.execute(sql, tuple(valores))
    conexao.commit()
    conexao.close()

    return "Evento atualizado com sucesso!"

def listar_eventos():
    conexao, cursor = conectar_banco()

    cursor.execute('SELECT id_evento, nome_evento, data_evento FROM eventos')
    eventos_banco = cursor.fetchall()
    conexao.close()

    lista_eventos = []
    for e in eventos_banco:
        lista_eventos.append({
            "id_evento": e[0],
            "nome_evento": e[1],
            "data_evento": e[2]
        })
            
    return lista_eventos

def deletar_evento(id_evento):
    conexao, cursor = conectar_banco()

    sql = 'DELETE FROM eventos WHERE id_evento = ?'
    cursor.execute(sql, (id_evento,))
    conexao.commit()
    conexao.close()

    return "Evento excluído do sistema!"


##### FINANCEIRO EVENTOS ######
def cadastrar_transacao_evento(id_evento, descricao, tipo, valor):
    conexao, cursor = conectar_banco()

    sql = '''
        INSERT INTO financeiro_eventos (id_evento, descricao, tipo, valor)
        VALUES (?, ?, ?, ?)
    '''
    cursor.execute(sql, (id_evento, descricao, tipo, valor))
    conexao.commit()
    conexao.close()
    
    return "Transação do evento registrada!"


##### AULAS AVULSAS ######
def cadastrar_aula_avulsa(aluno_nome, nome_professor, data_aula, valor_total_aula_avulsa, percentual_repasse=0):
    conexao, cursor = conectar_banco()

    cursor.execute("SELECT id_professor FROM professores WHERE nome LIKE ?", (f'%{nome_professor}%',))
    resultado = cursor.fetchone()

    if not resultado:
        conexao.close()
        return f"Ops! Não encontrei nenhum professor com o nome '{nome_professor}'."

    id_professor = resultado[0]
    repasse_prof = valor_total_aula_avulsa * (percentual_repasse / 100)
    lucro_caixa_avulso = valor_total_aula_avulsa - repasse_prof

    sql = '''
        INSERT INTO aulas_avulsas (aluno_nome, id_professor, data_aula, valor_total_aula_avulsa, repasse_prof, lucro_caixa_avulso)
        VALUES (?, ?, ?, ?, ?, ?)
    '''
    valores = (aluno_nome, id_professor, data_aula, valor_total_aula_avulsa, repasse_prof, lucro_caixa_avulso)

    cursor.execute(sql, valores)
    conexao.commit()
    conexao.close()

    return f"Aula avulsa registrada! Lucro para a escola: R${lucro_caixa_avulso:.2f}"

def listar_aulas_avulsas():
    conexao, cursor = conectar_banco()

    sql = '''
        SELECT 
            aulas_avulsas.id_aula,
            aulas_avulsas.aluno_nome,
            professores.nome,
            aulas_avulsas.data_aula,
            aulas_avulsas.valor_total_aula_avulsa,
            aulas_avulsas.repasse_prof,
            aulas_avulsas.lucro_caixa_avulso
        FROM aulas_avulsas
        LEFT JOIN professores ON aulas_avulsas.id_professor = professores.id_professor
    '''
    cursor.execute(sql)
    aulas_banco = cursor.fetchall()
    conexao.close()

    lista_aulas = []
    for aula in aulas_banco:
        lista_aulas.append({
            "id_aula": aula[0],
            "aluno_nome": aula[1],
            "nome_professor": aula[2] if aula[2] else "Prof. Desconhecido",
            "data_aula": aula[3],
            "valor_total": aula[4],
            "repasse": aula[5],
            "lucro": aula[6]
        })

    return lista_aulas

def atualizar_aula_avulsa(id_aula, **kwargs):
    if not kwargs:
        return "Nenhuma informação a ser atualizada."
    
    conexao, cursor = conectar_banco()
    campos_sql = []
    valores = []

    for coluna, novo_valor in kwargs.items():
        campos_sql.append(f"{coluna} = ?")
        valores.append(novo_valor)

    texto_set = ", ".join(campos_sql)
    sql = f'UPDATE aulas_avulsas SET {texto_set} WHERE id_aula = ?'
    valores.append(id_aula)

    cursor.execute(sql, tuple(valores))
    conexao.commit()
    conexao.close()

    return "Aula avulsa atualizada com sucesso!"

def deletar_aula_avulsa(id_aula):
    conexao, cursor = conectar_banco()

    sql = 'DELETE FROM aulas_avulsas WHERE id_aula = ?'
    cursor.execute(sql, (id_aula,))
    conexao.commit()
    conexao.close()

    return "Registro da aula avulsa excluído!"


##### PAGAMENTOS ######
def cadastrar_pagamento(id_aluno, id_turma, id_plano, data_vencimento_inicial, valor_final_mensal, status, data_pagamento=None, desconto_manual=0.0, tipo_desconto_manual=None, taxa_maquininha=0.0, duracao_meses=1):
    conexao, cursor = conectar_banco()

    data_vencimento = datetime.strptime(data_vencimento_inicial, "%d/%m/%Y") 

    sql = '''
        INSERT INTO pagamentos (id_aluno, id_turma, id_plano, mes_referencia, data_vencimento, desconto_manual, tipo_desconto_manual, taxa_maquininha, valor_final, status, data_pagamento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    for i in range(duracao_meses):
        nova_data_vencimento = adicionar_meses(data_vencimento, i)
        nova_data_str = nova_data_vencimento.strftime("%d/%m/%Y") 
        novo_mes_referencia = nova_data_vencimento.strftime("%m/%Y") 

        valores = (id_aluno, id_turma, id_plano, novo_mes_referencia, nova_data_str, desconto_manual, tipo_desconto_manual, taxa_maquininha, valor_final_mensal, status, data_pagamento)
        cursor.execute(sql, valores)

    conexao.commit()
    conexao.close()
    
    return f"Pagamento garantido! {duracao_meses} parcela(s) lançada(s) no sistema."

def atualizar_pagamento(id_pagamento, **kwargs):
    if not kwargs:
        return "Nenhuma informação a ser atualizada."
    
    conexao, cursor = conectar_banco()
    campos_sql = []
    valores = []

    for coluna, novo_valor in kwargs.items():
        campos_sql.append(f"{coluna} = ?")
        valores.append(novo_valor)

    texto_set = ", ".join(campos_sql)
    sql = f'UPDATE pagamentos SET {texto_set} WHERE id_pagamento = ?'
    valores.append(id_pagamento)

    cursor.execute(sql, tuple(valores))
    conexao.commit()
    conexao.close()

    return "Pagamento atualizado com sucesso!"

def listar_pagamentos():
    conexao, cursor = conectar_banco()

    sql = '''
        SELECT 
            pagamentos.id_pagamento,
            alunos.nome,
            turmas.nome_turma,
            planos.nome_plano,
            pagamentos.data_vencimento,
            pagamentos.valor_final,
            pagamentos.status,
            pagamentos.data_pagamento
        FROM pagamentos
        JOIN alunos ON pagamentos.id_aluno = alunos.id_aluno
        JOIN turmas ON pagamentos.id_turma = turmas.id_turma
        LEFT JOIN planos ON pagamentos.id_plano = planos.id_plano
    '''
    cursor.execute(sql)
    pagamentos_banco = cursor.fetchall()
    conexao.close()

    lista_pagamentos = []
    for pag in pagamentos_banco:
        lista_pagamentos.append({
            "id_pagamento": pag[0],
            "nome_aluno": pag[1],
            "nome_turma": pag[2],
            "nome_plano": pag[3] if pag[3] else "Sem Plano",
            "data_vencimento": pag[4],
            "valor_final": pag[5],
            "status": pag[6],
            "data_pagamento": pag[7] if pag[7] else ""
        })
            
    return lista_pagamentos

def deletar_pagamento(id_pagamento):
    conexao, cursor = conectar_banco()

    sql = 'DELETE FROM pagamentos WHERE id_pagamento = ?'
    cursor.execute(sql, (id_pagamento,))
    conexao.commit()
    conexao.close()

    return "Registro de pagamento excluído!"


##### INADIMPLENCIAS ######

def relatorio_inadimplencia():
    conexao, cursor = conectar_banco()

    sql = '''
       SELECT
            pagamentos.id_pagamento,
            alunos.nome,
            pagamentos.data_vencimento,
            pagamentos.valor_final,
            alunos.id_aluno
        FROM pagamentos
        JOIN alunos ON pagamentos.id_aluno = alunos.id_aluno
        WHERE pagamentos.status = 'Pendente' AND alunos.ativo = 1
    '''

    cursor.execute(sql)
    pendentes = cursor.fetchall()
    conexao.close()

    hoje = datetime.now()
    lista_inadimplentes = []

    for pag in pendentes:
        id_pag = pag[0]
        nome_aluno = pag[1]
        data_venc_str = pag[2]
        valor = pag[3]
        id_aluno = pag[4]
        
        try:
            data_venc = datetime.strptime(data_venc_str, "%d/%m/%Y")
            dias_atraso = (hoje - data_venc).days

            if dias_atraso > 0:
                lista_inadimplentes.append({
                    "id_pagamento": id_pag,
                    "nome_aluno": nome_aluno,
                    "id_aluno": id_aluno,
                    "dias_atraso": dias_atraso,
                    "valor_pendente": valor
                })
                
        except ValueError:
            pass

    return lista_inadimplentes