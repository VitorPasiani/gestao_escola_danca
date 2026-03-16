import sqlite3

###### ALUNOS ######
def cadastrar_aluno(nome, cpf=None, rg=None, endereco=None, data_nascimento=None, email=None, contato_1=None, contato_2=None, responsavel=None):
    #CONECTA COM O BANCO DE DADOS
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()
    
    sql = '''
        INSERT INTO alunos (nome, cpf, rg, endereco, data_nascimento, email, contato_1, contato_2, responsavel)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    valores = (nome, cpf, rg, endereco, data_nascimento, email, contato_1, contato_2, responsavel)

    cursor.execute(sql, valores)
    conexao.commit()
    conexao.close()

    print(f"Aluno {nome} cadastrado com sucesso!")

def atualizar_aluno(id_aluno, **kwargs):

    if not kwargs:
        print("Nenhuma informação a ser atualizada.")
        return
    
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    campos_sql = [] # Lista para armazenar os campos a serem atualizados
    valores = [] # Lista para armazenar os valores correspondentes aos campos

    for coluna, novo_valor in kwargs.items():
        campos_sql.append(f"{coluna} = ?") # Adiciona o campo e o placeholder para o valor
        valores.append(novo_valor) # Adiciona o novo valor à lista de valores

    texto_set = ", ".join(campos_sql) # Junta os campos em uma string para a cláusula SET

    sql = f'''
        UPDATE alunos
        SET {texto_set}
        WHERE id_aluno = ?
    '''

    valores.append(id_aluno) # Adiciona o id do aluno ao final da lista de valores para a cláusula WHERE

    cursor.execute(sql, tuple(valores)) # Executa a consulta de atualização com os valores fornecidos
    conexao.commit()
    conexao.close()

    print(f"Cadastro do aluno com ID {id_aluno} atualizado com sucesso!")

def listar_alunos():
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM alunos')
    alunos_salvos = cursor.fetchall()

    print("\n--- LISTA DE ALUNOS MATRICULADOS ---")
    for aluno in alunos_salvos:
        print(aluno)
        
    conexao.close()

def deletar_aluno(id_aluno):
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    sql = '''
        DELETE FROM alunos
        WHERE id_aluno = ?
    '''
    valores = (id_aluno,) # Tupla com o ID do aluno a ser deletado

    cursor.execute(sql, valores)
    conexao.commit()
    conexao.close()

    print(f"Cadastro do aluno com ID {id_aluno} foi excluído do sistema!")

###### PROFESSORES ######
def cadastrar_professor(nome, telefone=None, chave_pix=None):
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    sql = '''
        INSERT INTO professores (nome, telefone, chave_pix)
        VALUES (?, ?, ?)
    '''

    valores = (nome, telefone, chave_pix)

    cursor.execute(sql, valores)
    conexao.commit()
    conexao.close()

    print(f"Professor {nome} cadastrado com sucesso!")

def atualizar_professor(id_professor, **kwargs):
    if not kwargs:
        print("Nenhuma informação a ser atualizada.")
        return
    
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    campos_sql = []
    valores = []

    for coluna, novo_valor in kwargs.items():
        campos_sql.append(f"{coluna} = ?")
        valores.append(novo_valor)

    texto_set = ", ".join(campos_sql)

    sql = f'''
        UPDATE professores
        SET {texto_set}
        WHERE id_professor = ?
    '''

    valores.append(id_professor)

    cursor.execute(sql, tuple(valores))
    conexao.commit()
    conexao.close()

    print(f"Cadastro do professor com ID {id_professor} atualizado com sucesso!")

def listar_professores():
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM professores')
    professores_salvos = cursor.fetchall()

    print("\n--- LISTA DE PROFESSORES CADASTRADOS ---")
    for professor in professores_salvos:
        print(professor)
        
    conexao.close()

def deletar_professor(id_professor):
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    sql = '''
        DELETE FROM professores
        WHERE id_professor = ?
    '''
    valores = (id_professor,)

    cursor.execute(sql, valores)
    conexao.commit()
    conexao.close()

    print(f"Cadastro do professor com ID {id_professor} foi excluído do sistema!")

###### PLANOS ######
def cadastrar_plano(nome_plano, percentual_desconto):
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    sql = '''
        INSERT INTO planos (nome_plano, percentual_desconto)
        VALUES (?, ?)
    '''

    valores = (nome_plano, percentual_desconto)

    cursor.execute(sql, valores)
    conexao.commit()
    conexao.close()

    print(f"Plano '{nome_plano}' cadastrado com sucesso com {percentual_desconto}% de desconto!")

def atualizar_plano(id_plano, **kwargs):
    if not kwargs:
        print("Nenhuma informação a ser atualizada.")
        return
    
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    campos_sql = []
    valores = []

    for coluna, novo_valor in kwargs.items():
        campos_sql.append(f"{coluna} = ?")
        valores.append(novo_valor)

    texto_set = ", ".join(campos_sql)

    sql = f'''
        UPDATE planos
        SET {texto_set}
        WHERE id_plano = ?
    '''

    valores.append(id_plano)

    cursor.execute(sql, tuple(valores))
    conexao.commit()
    conexao.close()

    print(f"Cadastro do plano com ID {id_plano} atualizado com sucesso!")

def listar_planos():
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM planos')
    planos_salvos = cursor.fetchall()

    print("\n--- LISTA DE PLANOS CADASTRADOS ---")
    for plano in planos_salvos:
        print(plano)
        
    conexao.close()

def deletar_plano(id_plano):
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    sql = '''
        DELETE FROM planos
        WHERE id_plano = ?
    '''
    valores = (id_plano,)

    cursor.execute(sql, valores)
    conexao.commit()
    conexao.close()

    print(f"Cadastro do plano com ID {id_plano} foi excluído do sistema!")

###### TURMAS ######
def cadastrar_turma(nome_turma, tipo_gestao, id_professor=None, horario=None, dias_semana=None, valor_mensal_base=None, is_particular=False, cronograma=None, valor_por_aula=None):
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    sql = '''
        INSERT INTO turmas (nome_turma, id_professor, horario, dias_semana, valor_mensal_base, tipo_gestao, is_particular, cronograma, valor_por_aula)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    valores = (nome_turma, id_professor, horario, dias_semana, valor_mensal_base, tipo_gestao, is_particular, cronograma, valor_por_aula)

    cursor.execute(sql, valores)
    conexao.commit()
    conexao.close()

    print(f"Turma '{nome_turma}' cadastrada com sucesso!")

def atualizar_turma(id_turma, **kwargs):
    if not kwargs:
        print("Nenhuma informação a ser atualizada.")
        return
    
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    campos_sql = []
    valores = []

    for coluna, novo_valor in kwargs.items():
        campos_sql.append(f"{coluna} = ?")
        valores.append(novo_valor)

    texto_set = ", ".join(campos_sql)

    sql = f'''
        UPDATE turmas
        SET {texto_set}
        WHERE id_turma = ?
    '''

    valores.append(id_turma)

    cursor.execute(sql, tuple(valores))
    conexao.commit()
    conexao.close()

    print(f"Cadastro da turma com ID {id_turma} atualizado com sucesso!")

def listar_turmas():
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM turmas')
    turmas_salvas = cursor.fetchall()

    print("\n--- LISTA DE TURMAS CADASTRADAS ---")
    for turma in turmas_salvas:
        print(turma)
        
    conexao.close()

def deletar_turma(id_turma):
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    sql = '''
        DELETE FROM turmas
        WHERE id_turma = ?
    '''
    valores = (id_turma,)

    cursor.execute(sql, valores)
    conexao.commit()
    conexao.close()

    print(f"Cadastro da turma com ID {id_turma} foi excluído do sistema!")

##### EVENTOS ######
def cadastrar_evento(nome_evento, data_evento=None):
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    sql = '''
        INSERT INTO eventos (nome_evento, data_evento)
        VALUES (?, ?)
    '''
    valores = (nome_evento, data_evento)

    cursor.execute(sql, valores)
    conexao.commit()
    conexao.close()

    print(f"Evento '{nome_evento}' agendado com sucesso para {data_evento}!")

def atualizar_evento(id_evento, **kwargs):
    if not kwargs:
        print("Nenhuma informação a ser atualizada.")
        return
    
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    campos_sql = []
    valores = []

    for coluna, novo_valor in kwargs.items():
        campos_sql.append(f"{coluna} = ?")
        valores.append(novo_valor)

    texto_set = ", ".join(campos_sql)

    sql = f'''
        UPDATE eventos
        SET {texto_set}
        WHERE id_evento = ?
    '''

    valores.append(id_evento)

    cursor.execute(sql, tuple(valores))
    conexao.commit()
    conexao.close()

    print(f"Cadastro do evento com ID {id_evento} atualizado com sucesso!")

def listar_eventos():
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM eventos')
    eventos_salvos = cursor.fetchall()

    print("\n--- LISTA DE EVENTOS CADASTRADOS ---")
    for evento in eventos_salvos:
        print(evento)
        
    conexao.close()

def deletar_evento(id_evento):
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    sql = '''
        DELETE FROM eventos
        WHERE id_evento = ?
    '''
    valores = (id_evento,)

    cursor.execute(sql, valores)
    conexao.commit()
    conexao.close()

    print(f"Cadastro do evento com ID {id_evento} foi excluído do sistema!")

##### FINANCEIRO EVENTOS ######
def cadastrar_transacao_evento(id_evento, descricao, tipo, valor):
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    sql = '''
        INSERT INTO financeiro_eventos (id_evento, descricao, tipo, valor)
        VALUES (?, ?, ?, ?)
    '''
    valores = (id_evento, descricao, tipo, valor)

    cursor.execute(sql, valores)
    conexao.commit()
    conexao.close()