import sqlite3
import calendar
from datetime import datetime, timedelta
import re

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

def formatar_telefone(telefone):
    if not telefone:
        return "-"
    
    apenas_numeros = re.sub(r'\D', '', telefone)
    
    if len(apenas_numeros) == 11:
        return f"({apenas_numeros[:2]}) {apenas_numeros[2:7]}-{apenas_numeros[7:]}"
    
    elif len(apenas_numeros) == 10:
        return f"({apenas_numeros[:2]}) {apenas_numeros[2:6]}-{apenas_numeros[6:]}"
    
    return telefone

def verificar_conflito_sala(sala, dias_semana_lista, hora_inicio_nova, hora_fim_nova, id_turma_ignorada=None):
    conexao, cursor = conectar_banco()
    
    for dia in dias_semana_lista:
        sql = '''
            SELECT id_turma, nome_turma FROM turmas 
            WHERE sala = ? 
              AND dias_semana LIKE ? 
              AND ativo = 1
              AND hora_inicio < ? 
              AND hora_fim > ?
        '''
        cursor.execute(sql, (sala, f'%{dia}%', hora_fim_nova, hora_inicio_nova))
        resultados = cursor.fetchall()
        
        for res in resultados:
            id_conflito = res[0]
            nome_conflito = res[1]
            
            if id_turma_ignorada and id_conflito == id_turma_ignorada:
                continue
            else:
                conexao.close()
                return f"A turma '{nome_conflito}' já está usando a {sala} na {dia} neste horário!"
            
    conexao.close()
    return None

###### ALUNOS ######
def cadastrar_aluno(nome, cpf=None, rg=None, endereco=None, data_nascimento=None, email=None, contato_1=None, contato_2=None, responsavel=None):
    
    cpf = cpf if cpf else None
    rg = rg if rg else None
    email = email if email else None

    conexao, cursor = conectar_banco()
    
    sql = '''
        INSERT INTO alunos (nome, cpf, rg, endereco, data_nascimento, email, contato_1, contato_2, responsavel)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    valores = (nome, cpf, rg, endereco, data_nascimento, email, contato_1, contato_2, responsavel)

    try:
        cursor.execute(sql, valores)
        conexao.commit()
        return f"Aluno(a) {nome} cadastrado(a) com sucesso!"
    except sqlite3.IntegrityError as e:
        mensagem_erro = str(e).lower()
        if 'cpf' in mensagem_erro:
            raise ValueError("Já existe um aluno cadastrado com este CPF!")
        elif 'email' in mensagem_erro:
            raise ValueError("Este endereço de e-mail já está sendo usado por outro aluno!")
        elif 'rg' in mensagem_erro:
            raise ValueError("Este RG já está cadastrado no sistema!")
        else:
            raise ValueError("Erro de duplicidade: Um dado único já existe no sistema.")
    finally:
        conexao.close()

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
    cursor.execute('SELECT id_aluno, nome, cpf, data_nascimento, contato_1, contato_2, responsavel FROM alunos WHERE ativo = 1 ORDER BY nome ASC')
    alunos_banco = cursor.fetchall()
    conexao.close()

    lista_alunos = []
    for a in alunos_banco:
        lista_alunos.append({
            "id_aluno": a[0],
            "nome": a[1],
            "cpf": a[2],
            "data_nascimento": a[3],
            "contato_1": formatar_telefone(a[4]),
            "contato_2": formatar_telefone(a[5]),
            "responsavel": a[6] if a[6] else "-"
        })
    return lista_alunos

def listar_alunos_inativos():
    conexao, cursor = conectar_banco()
    cursor.execute('SELECT id_aluno, nome, cpf, data_nascimento, contato_1, contato_2, responsavel, motivo_inativacao FROM alunos WHERE ativo = 0 ORDER BY nome ASC')
    alunos_banco = cursor.fetchall()
    conexao.close()

    lista_inativos = []
    for a in alunos_banco:
        lista_inativos.append({
            "id_aluno": a[0],
            "nome": a[1],
            "cpf": a[2],
            "data_nascimento": a[3],
            "contato_1": formatar_telefone(a[4]),
            "contato_2": formatar_telefone(a[5]),
            "responsavel": a[6] if a[6] else "-",
            "motivo_inativacao": a[7] if a[7] else "Decisão do Aluno"
        })
    return lista_inativos

def inativar_aluno(id_aluno, motivo="Decisão do Aluno"):
    conexao, cursor = conectar_banco()

    sql = '''
        UPDATE alunos
        SET ativo = 0, motivo_inativacao = ?
        WHERE id_aluno = ?
    '''
    cursor.execute(sql, (motivo, id_aluno))
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

def buscar_aluno(id_aluno):
    conexao, cursor = conectar_banco()

    cursor.execute('SELECT * FROM alunos WHERE id_aluno = ?', (id_aluno,))
    
    nomes_colunas = [descricao[0] for descricao in cursor.description]
    
    resultado = cursor.fetchone()
    
    conexao.close()

    if resultado:
        aluno_dicionario = dict(zip(nomes_colunas, resultado))
        return aluno_dicionario
    
    return None

def aluno_ja_tem_vinculo(id_aluno):
    conexao, cursor = conectar_banco()
    cursor.execute("SELECT COUNT(*) FROM inscricoes WHERE id_aluno = ? AND status_academico = 'Ativo'", (id_aluno,))
    total = cursor.fetchone()[0]
    conexao.close()
    return total > 0

def verificar_vinculo_turma(id_aluno, id_turma):
    conexao, cursor = conectar_banco()
    cursor.execute("SELECT status_academico FROM inscricoes WHERE id_aluno = ? AND id_turma = ?", (id_aluno, id_turma))
    resultado = cursor.fetchone()
    conexao.close()
    
    if resultado:
        return resultado[0]
    return None

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

    cursor.execute('SELECT id_professor, nome, telefone, chave_pix FROM professores WHERE ativo = 1 ORDER BY nome ASC')
    profs_banco = cursor.fetchall()
    conexao.close()

    lista_professores = []
    for p in profs_banco:
        lista_professores.append({
            "id_professor": p[0],
            "nome": p[1],
            "telefone": formatar_telefone(p[2]) if p[2] else "-",
            "chave_pix": p[3] if p[3] else "-"
        })
            
    return lista_professores

def buscar_professor(id_professor):
    conexao, cursor = conectar_banco()

    cursor.execute('SELECT * FROM professores WHERE id_professor = ?', (id_professor,))
    nomes_colunas = [descricao[0] for descricao in cursor.description]
    resultado = cursor.fetchone()
    
    conexao.close()

    if resultado:
        return dict(zip(nomes_colunas, resultado))
    return None

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
    cursor.execute('SELECT id_plano, nome_plano, percentual_desconto, duracao_meses FROM planos WHERE ativo = 1 ORDER BY nome_plano ASC')
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

def listar_planos_inativos():
    conexao, cursor = conectar_banco()
    cursor.execute('SELECT id_plano, nome_plano, percentual_desconto, duracao_meses FROM planos WHERE ativo = 0 ORDER BY nome_plano ASC')
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

def inativar_plano(id_plano):
    conexao, cursor = conectar_banco()
    cursor.execute('UPDATE planos SET ativo = 0 WHERE id_plano = ?', (id_plano,))
    conexao.commit()
    conexao.close()
    return "Plano inativado com sucesso!"

def deletar_plano_definitivo(id_plano):
    conexao, cursor = conectar_banco()
    try:
        cursor.execute('DELETE FROM planos WHERE id_plano = ?', (id_plano,))
        conexao.commit()
        mensagem = ("Plano excluído permanentemente!", "success")
    except sqlite3.IntegrityError:
        mensagem = ("Não é possível excluir este plano permanentemente pois existem pagamentos atrelados a ele. Mantenha-o inativado.", "danger")
    finally:
        conexao.close()
    
    return mensagem

def buscar_plano(id_plano):
    conexao, cursor = conectar_banco()
    cursor.execute('SELECT * FROM planos WHERE id_plano = ?', (id_plano,))
    nomes_colunas = [descricao[0] for descricao in cursor.description]
    resultado = cursor.fetchone()
    conexao.close()
    if resultado:
        return dict(zip(nomes_colunas, resultado))
    return None

###### TURMAS ######
def cadastrar_turma(nome_turma, tipo_gestao, sala, id_professor=None, hora_inicio=None, hora_fim=None, dias_semana=None, valor_mensal_base=None, is_particular=False, cronograma=None, valor_por_aula=None):
    conexao, cursor = conectar_banco()

    sql = '''
        INSERT INTO turmas (nome_turma, id_professor, sala, hora_inicio, hora_fim, dias_semana, valor_mensal_base, tipo_gestao, is_particular, cronograma, valor_por_aula)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    valores = (nome_turma, id_professor, sala, hora_inicio, hora_fim, dias_semana, valor_mensal_base, tipo_gestao, is_particular, cronograma, valor_por_aula)

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
            turmas.id_turma, turmas.nome_turma, professores.nome,
            turmas.sala, turmas.hora_inicio, turmas.hora_fim,
            turmas.dias_semana, turmas.valor_mensal_base, turmas.tipo_gestao,
            turmas.is_particular, turmas.cronograma
        FROM turmas
        LEFT JOIN professores ON turmas.id_professor = professores.id_professor
        WHERE turmas.ativo = 1
        ORDER BY turmas.nome_turma ASC
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
            "sala": t[3],
            "horario": f"{t[4]} às {t[5]}" if t[4] else "Horário Dinâmico", 
            "dias_semana": t[6] if t[6] else "Grade Dinâmica",
            "valor_mensal_base": t[7],
            "tipo_gestao": t[8],
            "is_particular": t[9],
            "cronograma": t[10]
        })
        
    return lista_turmas

def listar_turmas_inativas():
    conexao, cursor = conectar_banco()
    sql = '''
        SELECT turmas.id_turma, turmas.nome_turma, professores.nome, turmas.sala, 
               turmas.hora_inicio, turmas.hora_fim, turmas.dias_semana, 
               turmas.valor_mensal_base, turmas.tipo_gestao
        FROM turmas
        LEFT JOIN professores ON turmas.id_professor = professores.id_professor
        WHERE turmas.ativo = 0
        ORDER BY turmas.nome_turma ASC
    '''
    cursor.execute(sql)
    turmas_banco = cursor.fetchall()
    conexao.close()

    lista_turmas = []
    for t in turmas_banco:
        lista_turmas.append({
            "id_turma": t[0], "nome_turma": t[1], "nome_professor": t[2] if t[2] else "Sem Professor",
            "sala": t[3], "horario": f"{t[4]} às {t[5]}", "dias_semana": t[6],
            "valor_mensal_base": t[7], "tipo_gestao": t[8]
        })
    return lista_turmas

def buscar_turma(id_turma):
    conexao, cursor = conectar_banco()
    cursor.execute('SELECT * FROM turmas WHERE id_turma = ?', (id_turma,))
    nomes_colunas = [descricao[0] for descricao in cursor.description]
    resultado = cursor.fetchone()
    conexao.close()
    if resultado:
        return dict(zip(nomes_colunas, resultado))
    return None

def inativar_turma(id_turma):
    conexao, cursor = conectar_banco()
    cursor.execute('UPDATE turmas SET ativo = 0 WHERE id_turma = ?', (id_turma,))
    conexao.commit()
    conexao.close()
    return "Turma inativada com sucesso!"

def deletar_turma_definitivo(id_turma):
    conexao, cursor = conectar_banco()
    try:
        cursor.execute('DELETE FROM turmas WHERE id_turma = ?', (id_turma,))
        conexao.commit()
        mensagem = ("Turma excluída permanentemente!", "success")
    except sqlite3.IntegrityError:
        mensagem = ("Não é possível excluir esta turma permanentemente pois existem pagamentos ou alunos atrelados a ela. Mantenha-a inativada.", "danger")
    finally:
        conexao.close()
    
    return mensagem

def listar_matriculas(status_alvo='Ativo'):
    conexao, cursor = conectar_banco()

    sql = '''
        SELECT 
            i.id_inscricao, 
            a.nome AS nome_aluno, 
            t.nome_turma, 
            p.nome AS nome_professor,
            i.data_inscricao, 
            i.status_pagamento_matricula, 
            i.status_academico
        FROM inscricoes i
        JOIN alunos a ON i.id_aluno = a.id_aluno
        JOIN turmas t ON i.id_turma = t.id_turma
        LEFT JOIN professores p ON t.id_professor = p.id_professor
        WHERE i.status_academico = ?
        ORDER BY a.nome ASC
    '''
    cursor.execute(sql, (status_alvo,))
    matriculas_banco = cursor.fetchall()
    conexao.close()

    lista_matriculas = []
    for m in matriculas_banco:
        lista_matriculas.append({
            "id_inscricao": m[0],
            "nome_aluno": m[1],
            "nome_turma": m[2],
            "nome_professor": m[3] if m[3] else "Sem Professor",
            "data_inscricao": m[4],
            "status_pagamento": m[5],
            "status_academico": m[6]
        })

    return lista_matriculas

def inativar_matricula(id_inscricao):
    conexao, cursor = conectar_banco()
    cursor.execute("UPDATE inscricoes SET status_academico = 'Inativo' WHERE id_inscricao = ?", (id_inscricao,))
    conexao.commit()
    conexao.close()
    return "Vínculo encerrado com sucesso. O histórico foi movido para as matrículas inativas."

def reativar_matricula(id_inscricao):
    conexao, cursor = conectar_banco()
    cursor.execute("UPDATE inscricoes SET status_academico = 'Ativo', status_pagamento_matricula = 'Pendente' WHERE id_inscricao = ?", (id_inscricao,))
    conexao.commit()
    conexao.close()
    return "Matrícula reativada! Verifique a necessidade de nova taxa de adesão."

##### PARTICULARES ######
def realizar_inscricao_aluno(id_aluno, id_turma, status_matricula):
    conexao, cursor = conectar_banco()
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    try:
        sql_ins = '''
            INSERT INTO inscricoes (id_aluno, id_turma, data_inscricao, status_pagamento_matricula)
            VALUES (?, ?, ?, ?)
        '''
        cursor.execute(sql_ins, (id_aluno, id_turma, data_hoje, status_matricula))
        
        if status_matricula == 'Pago':
            cursor.execute('UPDATE saldos_caixa SET saldo_matriculas = saldo_matriculas + 100.0 WHERE id_saldo = 1')
            
        conexao.commit()
        return "Inscrição realizada com sucesso!"
    except Exception as e:
        return f"Erro ao inscrever aluno: {str(e)}"
    finally:
        conexao.close()

def registrar_frequencia_particular(id_inscricao, data_aula, valor_aula):
    conexao, cursor = conectar_banco()
    sql = 'INSERT INTO frequencia_particulares (id_inscricao, data_aula, valor_aula_momento) VALUES (?, ?, ?)'
    
    try:
        cursor.execute(sql, (id_inscricao, data_aula, valor_aula))
        conexao.commit()
        return "Presença registrada! O valor será contabilizado no fechamento do mês."
    finally:
        conexao.close()

def listar_inscricoes_particulares():
    conexao, cursor = conectar_banco()
    sql = '''
        SELECT i.id_inscricao, a.nome, t.nome_turma, t.valor_por_aula
        FROM inscricoes i
        JOIN alunos a ON i.id_aluno = a.id_aluno
        JOIN turmas t ON i.id_turma = t.id_turma
        WHERE a.ativo = 1 AND t.ativo = 1 AND t.is_particular = 1
        ORDER BY a.nome ASC
    '''
    cursor.execute(sql)
    resultados = cursor.fetchall()
    conexao.close()
    return [{"id_inscricao": r[0], "nome_aluno": r[1], "nome_turma": r[2], "valor_aula": r[3]} for r in resultados]

def buscar_valor_aula_por_inscricao(id_inscricao):
    conexao, cursor = conectar_banco()
    sql = 'SELECT t.valor_por_aula FROM inscricoes i JOIN turmas t ON i.id_turma = t.id_turma WHERE i.id_inscricao = ?'
    cursor.execute(sql, (id_inscricao,))
    res = cursor.fetchone()
    conexao.close()
    return res[0] if res else 0.0

def listar_ultimos_checkins(limite=20):
    conexao, cursor = conectar_banco()
    sql = '''
        SELECT f.data_aula, a.nome, t.nome_turma, f.valor_aula_momento
        FROM frequencia_particulares f
        JOIN inscricoes i ON f.id_inscricao = i.id_inscricao
        JOIN alunos a ON i.id_aluno = a.id_aluno
        JOIN turmas t ON i.id_turma = t.id_turma
        ORDER BY f.id_frequencia DESC LIMIT ?
    '''
    cursor.execute(sql, (limite,))
    res = cursor.fetchall()
    conexao.close()
    return [{"data_aula": r[0], "nome_aluno": r[1], "nome_turma": r[2], "valor_aula_momento": r[3]} for r in res]

def listar_pendencias_particulares():
    conexao, cursor = conectar_banco()
    
    sql = '''
        SELECT 
            a.id_aluno, a.nome,
            t.nome_turma, 
            f.id_frequencia, f.data_aula, f.valor_aula_momento
        FROM frequencia_particulares f
        JOIN inscricoes i ON f.id_inscricao = i.id_inscricao
        JOIN alunos a ON i.id_aluno = a.id_aluno
        JOIN turmas t ON i.id_turma = t.id_turma
        WHERE f.faturado = 0
        ORDER BY a.nome ASC, f.data_aula ASC
    '''
    cursor.execute(sql)
    resultados = cursor.fetchall()
    conexao.close()

    alunos_pendentes = {}
    for res in resultados:
        id_aluno, nome_aluno, nome_turma, id_freq, data_aula, valor = res
        
        if id_aluno not in alunos_pendentes:
            alunos_pendentes[id_aluno] = {
                'nome': nome_aluno,
                'total_aulas': 0,
                'valor_total': 0.0,
                'aulas_detalhadas': []
            }
            
        alunos_pendentes[id_aluno]['total_aulas'] += 1
        alunos_pendentes[id_aluno]['valor_total'] += valor
        alunos_pendentes[id_aluno]['aulas_detalhadas'].append({
            'id_frequencia': id_freq,
            'turma': nome_turma,
            'data': data_aula,
            'valor': valor
        })
        
    return alunos_pendentes

def faturar_aulas_selecionadas(ids_frequencias, taxa_maquininha=0.0):
    if not ids_frequencias:
        return "Nenhuma aula foi selecionada."

    conexao, cursor = conectar_banco()
    ids_int = [int(i) for i in ids_frequencias]
    placeholders = ','.join(['?'] * len(ids_int))
    hoje_str = datetime.now().strftime("%d/%m/%Y")
    mes_ref = datetime.now().strftime("%m/%Y")

    sql_busca = f'''
        SELECT i.id_aluno, i.id_turma, SUM(f.valor_aula_momento)
        FROM frequencia_particulares f
        JOIN inscricoes i ON f.id_inscricao = i.id_inscricao
        WHERE f.id_frequencia IN ({placeholders})
        GROUP BY i.id_aluno, i.id_turma
    '''
    cursor.execute(sql_busca, ids_int)
    agrupados = cursor.fetchall()

    for grupo in agrupados:
        id_aluno, id_turma, valor_total = grupo
        
        sql_pag = '''
            INSERT INTO pagamentos (id_aluno, id_turma, mes_referencia, data_vencimento, taxa_maquininha, valor_final, status, data_pagamento)
            VALUES (?, ?, ?, ?, ?, ?, 'Pago', ?)
        '''
        cursor.execute(sql_pag, (id_aluno, id_turma, mes_ref, hoje_str, taxa_maquininha, valor_total, hoje_str))

        valor_liquido = valor_total - (valor_total * taxa_maquininha)
        cursor.execute('UPDATE saldos_caixa SET saldo_principal = saldo_principal + ? WHERE id_saldo = 1', (valor_liquido,))

    sql_update = f'UPDATE frequencia_particulares SET faturado = 1 WHERE id_frequencia IN ({placeholders})'
    cursor.execute(sql_update, ids_int)

    conexao.commit()
    conexao.close()
    return f"Sucesso! {len(ids_frequencias)} aulas faturadas. O valor líquido foi transferido para o Caixa Principal."

def quitar_taxa_matricula(id_inscricao, usar_maquininha=False, taxa_maquininha=0.0):
    conexao, cursor = conectar_banco()

    cursor.execute("UPDATE inscricoes SET status_pagamento_matricula = 'Pago' WHERE id_inscricao = ?", (id_inscricao,))

    valor_base = 100.0
    if usar_maquininha and taxa_maquininha > 0:
        valor_liquido = valor_base - (valor_base * taxa_maquininha)
    else:
        valor_liquido = valor_base

    cursor.execute('UPDATE saldos_caixa SET saldo_matriculas = saldo_matriculas + ? WHERE id_saldo = 1', (valor_liquido,))

    conexao.commit()
    conexao.close()
    
    return f"Taxa de matrícula quitada! +R$ {valor_liquido:.2f} adicionados ao Caixa Matrículas."

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

    cursor.execute('SELECT id_evento, nome_evento, data_evento, status FROM eventos ORDER BY nome_evento ASC')
    eventos_banco = cursor.fetchall()
    conexao.close()

    lista_eventos = []
    for e in eventos_banco:
        lista_eventos.append({
            "id_evento": e[0],
            "nome_evento": e[1],
            "data_evento": e[2],
            "status": e[3] if e[3] else "Aberto"
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

    cursor.execute("SELECT status, nome_evento FROM eventos WHERE id_evento = ?", (id_evento,))
    evento = cursor.fetchone()
    
    if evento[0] == 'Encerrado':
        conexao.close()
        raise ValueError("Este evento já foi encerrado. Não é possível adicionar novas transações.")

    sql = '''
        INSERT INTO financeiro_eventos (id_evento, descricao, tipo, valor)
        VALUES (?, ?, ?, ?)
    '''
    cursor.execute(sql, (id_evento, descricao, tipo, valor))
    conexao.commit()
    conexao.close()
    
    registrar_movimentacao_caixa('Eventos', tipo, valor, f"{evento[1]}: {descricao}")
    
    return "Transação do evento registrada!"

def deletar_transacao_evento(id_transacao, id_evento):
    conexao, cursor = conectar_banco()
    
    try:
        cursor.execute("SELECT status, nome_evento FROM eventos WHERE id_evento = ?", (id_evento,))
        evento = cursor.fetchone()
        
        if evento[0] == 'Encerrado':
            return "Ação bloqueada! Não é possível excluir lançamentos de um evento já encerrado.", "danger"

        cursor.execute("SELECT descricao, tipo, valor FROM financeiro_eventos WHERE id_transacao_evento = ?", (id_transacao,))
        transacao = cursor.fetchone()
        
        if transacao:
            desc_trans, tipo_trans, valor_trans = transacao
            
            cursor.execute("DELETE FROM financeiro_eventos WHERE id_transacao_evento = ?", (id_transacao,))
            conexao.commit()
            
            tipo_estorno = 'Saida' if tipo_trans == 'Entrada' else 'Entrada'
            registrar_movimentacao_caixa('Eventos', tipo_estorno, valor_trans, f"ESTORNO ({evento[1]}): {desc_trans}")

        return "Lançamento excluído com sucesso!", "warning"
        
    except Exception as e:
        conexao.rollback()
        return f"Erro ao excluir transação: {str(e)}", "danger"
    finally:
        conexao.close()

def buscar_balanco_evento(id_evento):
    conexao, cursor = conectar_banco()
    
    # Busca todas as transações
    cursor.execute("SELECT id_transacao_evento, descricao, tipo, valor FROM financeiro_eventos WHERE id_evento = ?", (id_evento,))
    transacoes = cursor.fetchall()
    
    # Busca status e nome
    cursor.execute("SELECT nome_evento, status FROM eventos WHERE id_evento = ?", (id_evento,))
    dados_evento = cursor.fetchone()
    conexao.close()
    
    total_entradas = 0.0
    total_saidas = 0.0
    lista_transacoes = []
    
    for t in transacoes:
        id_trans, desc, tipo, valor = t
        lista_transacoes.append({
            "id": id_trans, "descricao": desc, "tipo": tipo, "valor": valor
        })
        if tipo == 'Entrada':
            total_entradas += valor
        else:
            total_saidas += valor
            
    saldo_final = total_entradas - total_saidas
    
    return {
        "nome_evento": dados_evento[0] if dados_evento else "Evento Desconhecido",
        "status": dados_evento[1] if dados_evento else "Aberto",
        "transacoes": lista_transacoes,
        "total_entradas": total_entradas,
        "total_saidas": total_saidas,
        "saldo_final": saldo_final
    }

def encerrar_evento_e_transferir_saldo(id_evento):
    conexao, cursor = conectar_banco()
    
    try:
        cursor.execute("SELECT nome_evento, status FROM eventos WHERE id_evento = ?", (id_evento,))
        evento = cursor.fetchone()
        
        if not evento or evento[1] == 'Encerrado':
            return "O evento não existe ou já foi encerrado.", "warning"
            
        nome_evento = evento[0]

        cursor.execute("SELECT tipo, valor FROM financeiro_eventos WHERE id_evento = ?", (id_evento,))
        transacoes = cursor.fetchall()
        saldo = sum([t[1] if t[0] == 'Entrada' else -t[1] for t in transacoes])
        
        cursor.execute("UPDATE eventos SET status = 'Encerrado' WHERE id_evento = ?", (id_evento,))
        conexao.commit()
        
        if saldo > 0:
            registrar_movimentacao_caixa('Eventos', 'Transferencia', saldo, f"Repasse de Lucro: {nome_evento}", caixa_destino='Operacional')
        elif saldo < 0:
            registrar_movimentacao_caixa('Operacional', 'Transferencia', abs(saldo), f"Cobertura de Prejuízo: {nome_evento}", caixa_destino='Eventos')
            
        return f"Evento encerrado com sucesso! Saldo transferido.", "success"
        
    except Exception as e:
        conexao.rollback()
        return f"Erro ao encerrar evento: {str(e)}", "danger"
    finally:
        conexao.close()


##### AULAS AVULSAS ######
def cadastrar_aula_avulsa(aluno_nome, nome_professor, data_aula, valor_total_aula_avulsa, percentual_repasse=0, taxa_maquininha=0.0):
    conexao, cursor = conectar_banco()
    cursor.execute("SELECT id_professor FROM professores WHERE nome LIKE ?", (f'%{nome_professor}%',))
    resultado = cursor.fetchone()

    if not resultado:
        conexao.close()
        return f"Professor '{nome_professor}' não encontrado."

    id_professor = resultado[0]
    
    valor_liquido_real = valor_total_aula_avulsa - (valor_total_aula_avulsa * taxa_maquininha)
    
    repasse_prof = valor_liquido_real * (percentual_repasse / 100)
    
    lucro_caixa_avulso = valor_liquido_real - repasse_prof

    sql = '''
        INSERT INTO aulas_avulsas (aluno_nome, id_professor, data_aula, valor_total_aula_avulsa, taxa_maquininha, repasse_prof, lucro_caixa_avulso)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(sql, (aluno_nome, id_professor, data_aula, valor_total_aula_avulsa, taxa_maquininha, repasse_prof, lucro_caixa_avulso))

    cursor.execute('UPDATE saldos_caixa SET saldo_avulsas = saldo_avulsas + ? WHERE id_saldo = 1', (lucro_caixa_avulso,))

    conexao.commit()
    conexao.close()
    return f"Aula registrada! +R${lucro_caixa_avulso:.2f} no Caixa Avulsas."

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
        ORDER BY aulas_avulsas.data_aula DESC
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

def listar_faturas(mes_referencia):

    conexao, cursor = conectar_banco()

    sql = '''
        SELECT 
            f.id_fatura,
            a.nome AS nome_aluno,
            f.mes_referencia,
            f.data_vencimento,
            f.valor_bruto,
            f.desconto_aplicado,
            f.valor_final,
            f.status
        FROM faturas f
        JOIN alunos a ON f.id_aluno = a.id_aluno
        WHERE f.ativo = 1 AND f.mes_referencia = ?
        ORDER BY f.data_vencimento ASC
    '''
    cursor.execute(sql, (mes_referencia,))
    faturas_banco = cursor.fetchall()
    conexao.close()

    lista_faturas = []
    hoje = datetime.now().date()

    for f in faturas_banco:
        id_fatura, nome_aluno, mes_ref, data_venc_str, bruto, desconto, final, status_bd = f
        
        data_formatada = "-"
        status_visual = status_bd

        if data_venc_str:
            try:
                data_obj = datetime.strptime(data_venc_str, "%d/%m/%Y").date()
                data_formatada = data_venc_str
                
                if status_bd not in ['Pago', 'Cancelado'] and hoje > data_obj:
                    status_visual = 'Vencido'
            except ValueError:
                data_formatada = data_venc_str

        lista_faturas.append({
            "id_fatura": id_fatura,
            "nome_aluno": nome_aluno,
            "mes_referencia": mes_ref,
            "data_vencimento": data_formatada,
            "valor_bruto": bruto,
            "desconto_aplicado": desconto,
            "valor_final": final,
            "status": status_visual
        })
            
    return lista_faturas


def buscar_itens_fatura(id_fatura):
    conexao, cursor = conectar_banco()
    sql = '''
        SELECT 
            p.id_pagamento,
            t.nome_turma,
            pl.nome_plano,
            p.valor_final
        FROM pagamentos p
        JOIN turmas t ON p.id_turma = t.id_turma
        LEFT JOIN planos pl ON p.id_plano = pl.id_plano
        WHERE p.id_fatura = ?
    '''
    cursor.execute(sql, (id_fatura,))
    itens_banco = cursor.fetchall()
    conexao.close()

    lista_itens = []
    for i in itens_banco:
        lista_itens.append({
            "id_pagamento": i[0],
            "nome_turma": i[1],
            "nome_plano": i[2] if i[2] else "Avulso/Sem Plano",
            "valor": i[3]
        })
        
    return lista_itens

def baixar_fatura_unificada(id_fatura, usar_maquininha=False, taxa_maquininha=0.0):
    conexao, cursor = conectar_banco()

    try:
        hoje_str = datetime.now().strftime("%d/%m/%Y")

        cursor.execute("SELECT status FROM faturas WHERE id_fatura = ?", (id_fatura,))
        resultado = cursor.fetchone()
        
        if not resultado or resultado[0] == 'Pago':
            return "Aviso: Esta fatura já se encontra paga ou não existe.", "warning"

        sql_itens = '''
            SELECT p.id_pagamento, p.valor_final, t.tipo_gestao
            FROM pagamentos p
            JOIN turmas t ON p.id_turma = t.id_turma
            WHERE p.id_fatura = ?
        '''
        cursor.execute(sql_itens, (id_fatura,))
        itens_fatura = cursor.fetchall()

        lucro_liquido_escola = 0.0
        taxa_decimal = taxa_maquininha if usar_maquininha else 0.0

        for item in itens_fatura:
            id_pagamento, valor_final_item, tipo_gestao = item

            valor_pos_taxa = valor_final_item - (valor_final_item * taxa_decimal)

            repasse_prof = 0.0
            if tipo_gestao == 'Parceiro':
                repasse_prof = valor_pos_taxa * 0.75
            
            lucro_liquido_escola += (valor_pos_taxa - repasse_prof)

            cursor.execute('''
                UPDATE pagamentos
                SET status = 'Pago', data_pagamento = ?, taxa_maquininha = ?
                WHERE id_pagamento = ?
            ''', (hoje_str, taxa_decimal, id_pagamento))

        cursor.execute('''
            UPDATE faturas
            SET status = 'Pago', data_pagamento = ?, taxa_maquininha = ?
            WHERE id_fatura = ?
        ''', (hoje_str, taxa_decimal, id_fatura))

        cursor.execute('UPDATE saldos_caixa SET saldo_principal = saldo_principal + ? WHERE id_saldo = 1', (lucro_liquido_escola,))

        conexao.commit()
        return f"Pagamento registrado com sucesso! R$ {lucro_liquido_escola:.2f} transferidos para o Caixa Principal.", "success"

    except Exception as e:
        conexao.rollback()
        return f"Erro ao processar o pagamento: {str(e)}", "danger"
    finally:
        conexao.close()

def deletar_pagamento(id_pagamento):
    conexao, cursor = conectar_banco()

    sql = 'DELETE FROM pagamentos WHERE id_pagamento = ?'
    cursor.execute(sql, (id_pagamento,))
    conexao.commit()
    conexao.close()

    return "Registro de pagamento excluído!"

def processar_fechamento_mensal(mes_referencia):
    conexao, cursor = conectar_banco()
    
    sql_regulares = '''
        SELECT i.id_aluno, i.id_turma, t.valor_mensal_base, i.data_inscricao
        FROM inscricoes i
        JOIN turmas t ON i.id_turma = t.id_turma
        WHERE i.status_academico = 'Ativo' AND t.is_particular = 0
    '''
    cursor.execute(sql_regulares)
    regulares = cursor.fetchall()

    sql_particulares = '''
        SELECT i.id_aluno, i.id_turma, f.id_frequencia, f.valor_aula_momento, i.data_inscricao
        FROM frequencia_particulares f
        JOIN inscricoes i ON f.id_inscricao = i.id_inscricao
        JOIN turmas t ON i.id_turma = t.id_turma
        WHERE f.faturado = 0
    '''
    cursor.execute(sql_particulares)
    particulares = cursor.fetchall()

    ref_mes, ref_ano = map(int, mes_referencia.split('/'))
    data_ref_comparacao = datetime(ref_ano, ref_mes, 1)

    regulares_filtrados = []
    for reg in regulares:
        id_aluno, id_turma, valor, data_inscricao = reg
        if data_inscricao:
            _, insc_mes, insc_ano = map(int, data_inscricao.split('/'))
            data_insc_comparacao = datetime(insc_ano, insc_mes, 1)
            
            if data_ref_comparacao < data_insc_comparacao:
                continue 
        regulares_filtrados.append(reg)

    particulares_filtrados = []
    for part in particulares:
        id_aluno, id_turma, id_freq, valor, data_inscricao = part
        if data_inscricao:
            _, insc_mes, insc_ano = map(int, data_inscricao.split('/'))
            data_insc_comparacao = datetime(insc_ano, insc_mes, 1)
            
            if data_ref_comparacao < data_insc_comparacao:
                continue
        particulares_filtrados.append(part)

    alunos_fatura = {}
    
    for reg in regulares_filtrados:
        id_aluno, id_turma, valor, data_inscricao = reg
        if id_aluno not in alunos_fatura:
            dia_vencimento = data_inscricao.split('/')[0] if data_inscricao else '10'
            alunos_fatura[id_aluno] = {'regulares': [], 'particulares': [], 'dia_base': dia_vencimento}
            
        alunos_fatura[id_aluno]['regulares'].append({'id_turma': id_turma, 'valor': valor})

    for part in particulares_filtrados:
        id_aluno, id_turma, id_freq, valor, data_inscricao = part
        if id_aluno not in alunos_fatura:
            dia_vencimento = data_inscricao.split('/')[0] if data_inscricao else '10'
            alunos_fatura[id_aluno] = {'regulares': [], 'particulares': [], 'dia_base': dia_vencimento}
            
        alunos_fatura[id_aluno]['particulares'].append({'id_turma': id_turma, 'id_frequencia': id_freq, 'valor': valor})

    contador_faturas = 0

    for id_aluno, dados in alunos_fatura.items():
        
        valor_bruto_regular = sum([item['valor'] for item in dados['regulares']])
        valor_bruto_particular = sum([item['valor'] for item in dados['particulares']])
        valor_bruto_total = valor_bruto_regular + valor_bruto_particular
        
        desconto_aplicado = 0.0
        id_plano_usado = None
        
        if len(dados['regulares']) >= 2:
            desconto_aplicado = valor_bruto_regular * 0.10
            id_plano_usado = 5 
            
        valor_final = valor_bruto_total - desconto_aplicado

        if valor_final <= 0:
            continue

        cursor.execute("SELECT id_fatura FROM faturas WHERE id_aluno = ? AND mes_referencia = ?", (id_aluno, mes_referencia))
        if cursor.fetchone():
            continue

        dia_str = dados['dia_base']
        try:
            datetime.strptime(f"{dia_str}/{mes_referencia}", "%d/%m/%Y")
            data_vencimento = f"{dia_str}/{mes_referencia}"
        except ValueError:
            mes, ano = mes_referencia.split('/')
            ultimo_dia = calendar.monthrange(int(ano), int(mes))[1]
            data_vencimento = f"{ultimo_dia:02d}/{mes_referencia}"

        sql_fatura = '''
            INSERT INTO faturas (id_aluno, mes_referencia, data_vencimento, valor_bruto, desconto_aplicado, valor_final, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Pendente')
        '''
        cursor.execute(sql_fatura, (id_aluno, mes_referencia, data_vencimento, valor_bruto_total, desconto_aplicado, valor_final))
        id_fatura = cursor.lastrowid
        
        for reg in dados['regulares']:
            valor_com_rateio = reg['valor'] - (desconto_aplicado / len(dados['regulares'])) if desconto_aplicado > 0 else reg['valor']
            
            sql_pag = '''
                INSERT INTO pagamentos (id_fatura, id_aluno, id_turma, id_plano, mes_referencia, data_vencimento, valor_final, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Pendente')
            '''
            cursor.execute(sql_pag, (id_fatura, id_aluno, reg['id_turma'], id_plano_usado, mes_referencia, data_vencimento, valor_com_rateio))
            
        ids_frequencias = []
        for part in dados['particulares']:
            sql_pag_part = '''
                INSERT INTO pagamentos (id_fatura, id_aluno, id_turma, mes_referencia, data_vencimento, valor_final, status)
                VALUES (?, ?, ?, ?, ?, ?, 'Pendente')
            '''
            cursor.execute(sql_pag_part, (id_fatura, id_aluno, part['id_turma'], mes_referencia, data_vencimento, part['valor']))
            ids_frequencias.append(str(part['id_frequencia']))
            
        if ids_frequencias:
            placeholders = ','.join(['?'] * len(ids_frequencias))
            cursor.execute(f"UPDATE frequencia_particulares SET faturado = 1 WHERE id_frequencia IN ({placeholders})", ids_frequencias)
            
        contador_faturas += 1

    conexao.commit()
    conexao.close()
    
    return f"Fechamento de {mes_referencia} concluído! {contador_faturas} faturas foram geradas com sucesso."

##### INADIMPLENCIAS ######
def listar_detalhes_inadimplencia():
    conexao, cursor = conectar_banco()
    
    sql = '''
        SELECT 
            p.id_pagamento, a.nome, t.nome_turma, t.valor_mensal_base,
            p.data_vencimento, p.valor_final, a.id_aluno, t.is_particular
        FROM pagamentos p
        JOIN alunos a ON p.id_aluno = a.id_aluno
        JOIN turmas t ON p.id_turma = t.id_turma
        WHERE p.status = 'Pendente' AND a.ativo = 1
    '''
    cursor.execute(sql)
    pendentes = cursor.fetchall()
    conexao.close()

    hoje = datetime.now()
    relatorio = []

    for pag in pendentes:
        id_pag, nome_aluno, nome_turma, valor_base, data_venc_str, valor_final_registrado, id_aluno, is_particular = pag
        
        try:
            data_limite = datetime.strptime(data_venc_str, "%d/%m/%Y")
            atraso = (hoje - data_limite).days
            
            valor_atualizado = valor_final_registrado
            status_atraso = "Pendente"
            multa_aplicada = False
            pode_inativar = False

            if atraso > 0:
                if not is_particular:
                    status_atraso = "Em Atraso"
                    if atraso > 10:
                        valor_atualizado = valor_base * 1.10
                        multa_aplicada = True
                
                else:
                    status_atraso = "Atraso (Pós-Pago)"
                
                if atraso > 30:
                    pode_inativar = True
            
            relatorio.append({
                "id_pagamento": id_pag,
                "id_aluno": id_aluno,
                "aluno": nome_aluno,
                "turma": nome_turma,
                "data_limite": data_venc_str,
                "valor_original": valor_final_registrado,
                "valor_atualizado": valor_atualizado,
                "dias_atraso": atraso if atraso > 0 else 0,
                "status": status_atraso,
                "multa_aplicada": multa_aplicada,
                "pode_inativar": pode_inativar,
                "is_particular": bool(is_particular)
            })
        except Exception as e:
            continue
            
    return relatorio

def executar_limpeza_inadimplentes():
    inadimplentes = listar_detalhes_inadimplencia()
    alunos_para_inativar = [i['id_aluno'] for i in inadimplentes if i['pode_inativar']]
    
    contador = 0
    for id_aluno in set(alunos_para_inativar):
        inativar_aluno(id_aluno, motivo="Inadimplência")
        contador += 1
        
    return f"Limpeza concluída! {contador} alunos foram inativados por inadimplência."

##### FINACEIRO #####
def gerar_relatorio_dre(mes_referencia, despesas_fixas=0.0, retencao_caixa=0.0):
    conexao, cursor = conectar_banco()
    
    sql_mensalidades = '''
        SELECT SUM(p.valor_final) 
        FROM pagamentos p 
        WHERE p.mes_referencia = ? AND p.status = 'Pago'
    '''
    cursor.execute(sql_mensalidades, (mes_referencia,))
    receita_mensalidades = cursor.fetchone()[0] or 0.0
    
    sql_repasses = '''
        SELECT SUM((p.valor_final - (p.valor_final * IFNULL(p.taxa_maquininha, 0.0))) * 0.75) 
        FROM pagamentos p
        JOIN turmas t ON p.id_turma = t.id_turma
        WHERE p.mes_referencia = ? AND p.status = 'Pago' AND t.tipo_gestao = 'Parceiro'
    '''
    cursor.execute(sql_repasses, (mes_referencia,))
    repasse_mensalidades = cursor.fetchone()[0] or 0.0

    busca_mes = f"%{mes_referencia}" 
    sql_avulsas = '''
        SELECT SUM(lucro_caixa_avulso), SUM(repasse_prof)
        FROM aulas_avulsas
        WHERE data_aula LIKE ?
    '''
    cursor.execute(sql_avulsas, (busca_mes,))
    res_avulsas = cursor.fetchone()
    lucro_escola_avulsas = res_avulsas[0] or 0.0
    repasse_prof_avulsas = res_avulsas[1] or 0.0
    
    conexao.close()

    receita_total_avulsas = lucro_escola_avulsas + repasse_prof_avulsas
    receita_bruta_total = receita_mensalidades + receita_total_avulsas
    
    total_repasses = repasse_mensalidades + repasse_prof_avulsas
    receita_liquida_escola = receita_bruta_total - total_repasses
    
    lucro_operacional = receita_liquida_escola - despesas_fixas
    
    valor_distribuir = lucro_operacional - retencao_caixa
    repasse_socias = valor_distribuir / 2 if valor_distribuir > 0 else 0.0

    return {
        "mes_referencia": mes_referencia,
        "receita_bruta": receita_bruta_total,
        "total_repasses": total_repasses,
        "receita_liquida_escola": receita_liquida_escola,
        "despesas_fixas": despesas_fixas,
        "lucro_operacional": lucro_operacional,
        "retencao_caixa": retencao_caixa,
        "repasse_socias": repasse_socias
    }

def consultar_saldos():
    conexao, cursor = conectar_banco()
    cursor.execute('SELECT saldo_principal, saldo_matriculas, saldo_avulsas, saldo_eventos, saldo_reserva FROM saldos_caixa WHERE id_saldo = 1')
    resultado = cursor.fetchone()
    conexao.close()
    
    if resultado:
        return {
            "Principal": resultado[0], 
            "Matriculas": resultado[1], 
            "Avulsas": resultado[2], 
            "Eventos": resultado[3], 
            "Reserva": resultado[4]
        }
    return {"Principal": 0.0, "Matriculas": 0.0, "Avulsas": 0.0, "Eventos": 0.0, "Reserva": 0.0}

def listar_movimentacoes_caixa():
    conexao, cursor = conectar_banco()
    cursor.execute('''
        SELECT caixa_alvo, tipo_movimentacao, valor, descricao, data_movimentacao, caixa_destino_transferencia 
        FROM movimentacoes_caixa 
        ORDER BY id_movimentacao DESC LIMIT 100
    ''')
    resultados = cursor.fetchall()
    conexao.close()
    
    historico = []
    for r in resultados:
        historico.append({
            "caixa_alvo": r[0],
            "tipo": r[1],
            "valor": r[2],
            "descricao": r[3],
            "data": r[4],
            "caixa_destino": r[5] if r[5] else "-"
        })
    return historico

def registrar_saque(caixa_origem, descricao, valor):
    conexao, cursor = conectar_banco()
    
    saldos = consultar_saldos()
    saldo_atual = saldos.get(caixa_origem, 0.0)
    
    if valor > saldo_atual:
        conexao.close()
        return f"Erro: Saldo insuficiente no caixa '{caixa_origem}'.", "danger"
        
    coluna = ""
    if caixa_origem == "Principal": coluna = "saldo_principal"
    elif caixa_origem == "Matriculas": coluna = "saldo_matriculas"
    elif caixa_origem == "Avulsas": coluna = "saldo_avulsas"
    
    sql_update = f'UPDATE saldos_caixa SET {coluna} = {coluna} - ? WHERE id_saldo = 1'
    cursor.execute(sql_update, (valor,))
    
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    sql_insert = 'INSERT INTO historico_saques (caixa_origem, descricao, valor, data_saque) VALUES (?, ?, ?, ?)'
    cursor.execute(sql_insert, (caixa_origem, descricao, valor, data_hoje))
    
    conexao.commit()
    conexao.close()
    return f"Saque de R$ {valor:.2f} registrado com sucesso!", "success"

def registrar_movimentacao_caixa(caixa_nome, tipo, valor, descricao, caixa_destino=None):
    """
    Motor Central Financeiro:
    caixa_nome: 'Operacional', 'Matriculas', 'Avulsas', 'Eventos', 'Reserva'
    tipo: 'Entrada', 'Saida', 'Transferencia'
    """
    conexao, cursor = conectar_banco()
    hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Mapeamento de colunas para o SQL dinâmico
    mapa_colunas = {
        'Operacional': 'saldo_principal',
        'Matriculas': 'saldo_matriculas',
        'Avulsas': 'saldo_avulsas',
        'Eventos': 'saldo_eventos',
        'Reserva': 'saldo_reserva'
    }

    try:
        coluna_origem = mapa_colunas[caixa_nome]
        
        # 1. Se for SAÍDA ou TRANSFERÊNCIA, checar saldo
        if tipo in ['Saida', 'Transferencia']:
            cursor.execute(f"SELECT {coluna_origem} FROM saldos_caixa WHERE id_saldo = 1")
            saldo_atual = cursor.fetchone()[0]
            if valor > saldo_atual:
                return f"Saldo insuficiente no Caixa {caixa_nome}!", "danger"

        # 2. Executar a atualização de Saldo
        if tipo == 'Entrada':
            cursor.execute(f"UPDATE saldos_caixa SET {coluna_origem} = {coluna_origem} + ? WHERE id_saldo = 1", (valor,))
        
        elif tipo == 'Saida':
            cursor.execute(f"UPDATE saldos_caixa SET {coluna_origem} = {coluna_origem} - ? WHERE id_saldo = 1", (valor,))
        
        elif tipo == 'Transferencia' and caixa_destino:
            coluna_destino = mapa_colunas[caixa_destino]
            # Tira de um
            cursor.execute(f"UPDATE saldos_caixa SET {coluna_origem} = {coluna_origem} - ? WHERE id_saldo = 1", (valor,))
            # Põe no outro
            cursor.execute(f"UPDATE saldos_caixa SET {coluna_destino} = {coluna_destino} + ? WHERE id_saldo = 1", (valor,))
        
        # 3. Registrar no Histórico Unificado
        sql_hist = '''
            INSERT INTO movimentacoes_caixa (caixa_alvo, tipo_movimentacao, valor, descricao, data_movimentacao, caixa_destino_transferencia)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(sql_hist, (caixa_nome, tipo, valor, descricao, hoje, caixa_destino))
        
        conexao.commit()
        return "Movimentação realizada com sucesso!", "success"
    except Exception as e:
        conexao.rollback()
        return f"Erro financeiro: {str(e)}", "danger"
    finally:
        conexao.close()

def cadastrar_despesa(descricao, tipo, valor, vencimento, mes_ref):
    conexao, cursor = conectar_banco()
    sql = '''
        INSERT INTO despesas (descricao, tipo_despesa, valor, data_vencimento, mes_referencia)
        VALUES (?, ?, ?, ?, ?)
    '''
    cursor.execute(sql, (descricao, tipo, valor, vencimento, mes_ref))
    conexao.commit()
    conexao.close()
    return "Despesa registrada com sucesso!"

def clonar_despesas_mes_anterior(mes_novo, mes_anterior):
    conexao, cursor = conectar_banco()
    
    cursor.execute('SELECT descricao, tipo_despesa, valor FROM despesas WHERE mes_referencia = ? AND ativo = 1', (mes_anterior,))
    itens_anteriores = cursor.fetchall()
    
    contador = 0
    for desc, tipo, valor in itens_anteriores:
        valor_final = valor if tipo == 'Fixa' else 0.0
        
        sql = '''
            INSERT INTO despesas (descricao, tipo_despesa, valor, mes_referencia, status_pagamento)
            VALUES (?, ?, ?, ?, 'Pendente')
        '''
        cursor.execute(sql, (desc, tipo, valor_final, mes_novo))
        contador += 1
        
    conexao.commit()
    conexao.close()
    return f"Sucesso! {contador} despesas foram importadas do mês anterior."

def listar_despesas(mes_referencia):
    conexao, cursor = conectar_banco()
    sql = '''
        SELECT id_despesa, descricao, tipo_despesa, valor, data_vencimento, status_pagamento
        FROM despesas
        WHERE mes_referencia = ? AND ativo = 1
        ORDER BY status_pagamento DESC, data_vencimento ASC
    '''
    cursor.execute(sql, (mes_referencia,))
    resultados = cursor.fetchall()
    conexao.close()

    lista = []
    hoje = datetime.now().date()

    for r in resultados:
        id_despesa, descricao, tipo, valor, data_venc_str, status_bd = r
        
        data_formatada = "-"
        status_visual = status_bd

        if data_venc_str:
            try:
                data_obj = datetime.strptime(data_venc_str, "%Y-%m-%d").date()
                
                data_formatada = data_obj.strftime("%d/%m/%Y")
                
                if status_bd != 'Pago' and hoje > data_obj:
                    status_visual = 'Vencido'
                    
            except ValueError:
                data_formatada = data_venc_str

        lista.append({
            "id_despesa": id_despesa,
            "descricao": descricao,
            "tipo_despesa": tipo,
            "valor": valor,
            "data_vencimento": data_formatada,
            "status_pagamento": status_visual
        })
        
    return lista

def quitar_despesa(id_despesa):
    conexao, cursor = conectar_banco()
    
    # 1. Busca os dados da despesa
    cursor.execute("SELECT valor, descricao, status_pagamento FROM despesas WHERE id_despesa = ?", (id_despesa,))
    res = cursor.fetchone()
    
    if not res:
        conexao.close()
        return "Erro: Despesa não encontrada.", "danger"
    
    valor_despesa, descricao, status_atual = res
    conexao.close() # Fechamos aqui para não dar conflito, pois a função abaixo abrirá outra

    if status_atual == 'Pago':
        return "Esta despesa já foi baixada anteriormente.", "warning"

    # 2. USA O MOTOR CENTRAL (registrar_movimentacao_caixa)
    # Isso já garante: Checagem de Saldo + Baixa no Saldo + Registro no Livro Diário
    mensagem, categoria = registrar_movimentacao_caixa(
        caixa_nome='Operacional', 
        tipo='Saida', 
        valor=valor_despesa, 
        descricao=f"Pagto Despesa: {descricao}"
    )

    # 3. Se o motor deu ok, atualiza o status da despesa para 'Pago'
    if categoria == 'success':
        conexao, cursor = conectar_banco()
        cursor.execute("UPDATE despesas SET status_pagamento = 'Pago' WHERE id_despesa = ?", (id_despesa,))
        conexao.commit()
        conexao.close()
        return f"Despesa '{descricao}' paga com sucesso! Registrada no Livro Diário.", "success"
    else:
        return mensagem, categoria

def atualizar_despesa(id_despesa, descricao, tipo_despesa, valor, data_vencimento, mes_referencia):
    conexao, cursor = conectar_banco()
    sql = '''
        UPDATE despesas 
        SET descricao = ?, tipo_despesa = ?, valor = ?, data_vencimento = ?, mes_referencia = ?
        WHERE id_despesa = ?
    '''
    cursor.execute(sql, (descricao, tipo_despesa, valor, data_vencimento, mes_referencia, id_despesa))
    conexao.commit()
    conexao.close()
    return "Despesa atualizada com sucesso!"

def excluir_despesa(id_despesa):
    conexao, cursor = conectar_banco()
    cursor.execute("UPDATE despesas SET ativo = 0 WHERE id_despesa = ?", (id_despesa,))
    conexao.commit()
    conexao.close()
    return "Despesa excluída do painel!"
