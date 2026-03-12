import sqlite3

def inicializar_banco():
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            id_aluno INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            rg TEXT,
            endereco TEXT,
            data_nascimento TEXT,
            email TEXT,
            contato_1 TEXT,
            contato_2 TEXT,
            responsavel TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS professores (
            id_professor INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            chave_pix TEXT UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planos (
            id_plano INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_plano TEXT NOT NULL,
            percentual_desconto REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS turmas (
            id_turma INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_turma TEXT NOT NULL,
            id_professor INTEGER,
            horario TEXT,
            dias_semana TEXT,
            valor_mensal_base REAL,
            tipo_gestao TEXT NOT NULL,
            is_particular BOOLEAN,
            cronograma TEXT,
            valor_por_aula REAL,

            FOREIGN KEY (id_professor) REFERENCES professores (id_professor)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagamentos (
            id_pagamento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_aluno INTEGER,
            id_turma INTEGER,
            id_plano INTEGER,
            mes_referencia TEXT,
            data_vencimento TEXT,
            desconto_manual REAL,
            tipo_desconto_manual TEXT,
            taxa_maquininha REAL,
            valor_final REAL,
            status TEXT,
                
            FOREIGN KEY (id_aluno) REFERENCES alunos (id_aluno),
            FOREIGN KEY (id_turma) REFERENCES turmas (id_turma),
            FOREIGN KEY (id_plano) REFERENCES planos (id_plano)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aulas_avulsas (
            id_aula INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_nome TEXT NOT NULL,
            id_professor INTEGER,
            data_aula TEXT NOT NULL,
            valor_total_aula_avulsa REAL NOT NULL,
            repasse_prof REAL NOT NULL,
            lucro_caixa_avulso REAL NOT NULL,
                
            FOREIGN KEY (id_professor) REFERENCES professores (id_professor)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eventos (
            id_evento INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_evento TEXT NOT NULL,
            receitas REAL NOT NULL,
            despesas REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saldos_caixa (
            id_saldo INTEGER PRIMARY KEY AUTOINCREMENT,
            saldo_principal REAL DEFAULT 0.0,
            saldo_matriculas REAL DEFAULT 0.0,
            saldo_avulsas REAL DEFAULT 0.0
        )
    ''')

    cursor.execute('SELECT COUNT(*) FROM saldos_caixa')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO saldos_caixa (saldo_principal, saldo_matriculas, saldo_avulsas) VALUES (0.0, 0.0, 0.0)')

    conexao.commit()
    conexao.close()
    print("Banco de dados 'escola_danca.db' criado e tabelas estruturadas com sucesso!")

if __name__ == '__main__':
    inicializar_banco()