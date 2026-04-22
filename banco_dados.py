import sqlite3

def inicializar_banco():
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    # 1. LIGANDO O FISCAL DE CHAVES ESTRANGEIRAS
    cursor.execute('PRAGMA foreign_keys = ON;')

    # TABELA ALUNOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            id_aluno INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE,
            rg TEXT UNIQUE,
            endereco TEXT,
            data_nascimento TEXT,
            email TEXT,
            contato_1 TEXT,
            contato_2 TEXT,
            responsavel TEXT,
            ativo INTEGER DEFAULT 1,
            motivo_inativacao TEXT DEFAULT 'Decisão do Aluno'
        )
    ''')

    # TABELA PROFESSORES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS professores (
            id_professor INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            chave_pix TEXT,
            ativo INTEGER DEFAULT 1
        )
    ''')

    # TABELA PLANOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planos (
            id_plano INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_plano TEXT NOT NULL,
            percentual_desconto REAL NOT NULL,
            duracao_meses INTEGER DEFAULT 1,
            ativo INTEGER DEFAULT 1
        )
    ''')

    # TABELA TURMAS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS turmas (
            id_turma INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_turma TEXT NOT NULL,
            id_professor INTEGER,
            sala TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fim TEXT NOT NULL,
            dias_semana TEXT,
            valor_mensal_base REAL,
            tipo_gestao TEXT NOT NULL,
            is_particular BOOLEAN,
            cronograma TEXT,
            valor_por_aula REAL,
            ativo INTEGER DEFAULT 1,
            
            FOREIGN KEY (id_professor) REFERENCES professores (id_professor)
        )
    ''')

    # TABELA INSCRIÇÕES
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inscricoes (
        id_inscricao INTEGER PRIMARY KEY AUTOINCREMENT,
        id_aluno INTEGER,
        id_turma INTEGER,
        data_inscricao TEXT,
        status_pagamento_matricula TEXT DEFAULT 'Pendente', -- 'Pago' ou 'Pendente'
        status_academico TEXT DEFAULT 'Ativo', -- 'Ativo', 'Suspenso', 'Inativo'
        ativo INTEGER DEFAULT 1,
        FOREIGN KEY (id_aluno) REFERENCES alunos (id_aluno),
        FOREIGN KEY (id_turma) REFERENCES turmas (id_turma)
    )
''')

    # TABELA FREQUÊNCIA PARTICULARES
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS frequencia_particulares (
        id_frequencia INTEGER PRIMARY KEY AUTOINCREMENT,
        id_inscricao INTEGER,
        data_aula TEXT NOT NULL,
        valor_aula_momento REAL,
        faturado INTEGER DEFAULT 0,
        FOREIGN KEY (id_inscricao) REFERENCES inscricoes (id_inscricao)
    )
''')

    # TABELA PAGAMENTOS
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
            data_pagamento TEXT,
                
            FOREIGN KEY (id_aluno) REFERENCES alunos (id_aluno),
            FOREIGN KEY (id_turma) REFERENCES turmas (id_turma),
            FOREIGN KEY (id_plano) REFERENCES planos (id_plano)
        )
    ''')

    # TABELA AULAS AVULSAS (Adicionado taxa_maquininha)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aulas_avulsas (
            id_aula INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_nome TEXT NOT NULL,
            id_professor INTEGER NOT NULL,
            data_aula TEXT NOT NULL,
            valor_total_aula_avulsa REAL NOT NULL,
            taxa_maquininha REAL DEFAULT 0.0, -- NOVA COLUNA (Porcentagem, ex: 0.05 para 5%)
            repasse_prof REAL NOT NULL,
            lucro_caixa_avulso REAL NOT NULL,
                
            FOREIGN KEY (id_professor) REFERENCES professores (id_professor)
        )
    ''')

    # TABELA EVENTOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eventos (
            id_evento INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_evento TEXT NOT NULL,
            data_evento TEXT NOT NULL
        )
    ''')

    # TABELA FINANCEIRO EVENTOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS financeiro_eventos (
            id_transacao_evento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_evento INTEGER,
            descricao TEXT NOT NULL,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
                
            FOREIGN KEY (id_evento) REFERENCES eventos (id_evento)
        )
    ''')

# TABELA HISTORICO DE SAQUES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_saques (
            id_saque INTEGER PRIMARY KEY AUTOINCREMENT,
            caixa_origem TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data_saque TEXT NOT NULL
        )
    ''')

# TABELA SALDOS CAIXA (Adicionado saldo_reserva)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saldos_caixa (
            id_saldo INTEGER PRIMARY KEY AUTOINCREMENT,
            saldo_principal REAL DEFAULT 0.0,
            saldo_matriculas REAL DEFAULT 0.0,
            saldo_avulsas REAL DEFAULT 0.0,
            saldo_reserva REAL DEFAULT 0.0 -- O 4º CAIXA DE SEGURANÇA
        )
    ''')

    cursor.execute('SELECT COUNT(*) FROM saldos_caixa')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO saldos_caixa (saldo_principal, saldo_matriculas, saldo_avulsas, saldo_reserva) VALUES (0.0, 0.0, 0.0, 0.0)')

    conexao.commit()
    conexao.close()
    print("Banco de dados 'escola_danca.db' criado e tabelas estruturadas com sucesso!")

if __name__ == '__main__':
    inicializar_banco()