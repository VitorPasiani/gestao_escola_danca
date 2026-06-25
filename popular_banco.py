import sqlite3

def popular_banco_seed():
    print("🌱 Iniciando o plantio de dados (SEED) no banco...\n")
    conexao = sqlite3.connect('escola_danca.db')
    cursor = conexao.cursor()

    try:
        # ==========================================
        # 1. PROFESSORES
        # ==========================================
        professores = [
            ("Juliana (Jazz)", "11999999999", "juliana@pix.com"),
            ("Marcos (Hip Hop)", "11988888888", "marcos@pix.com"),
            ("Ana (Ballet)", "11977777777", "ana@pix.com"),
            ("Roberto (Contemporâneo)", "11966666666", "roberto@pix.com")
        ]
        cursor.executemany('INSERT INTO professores (nome, telefone, chave_pix) VALUES (?, ?, ?)', professores)

        # ==========================================
        # 2. PLANOS
        # ==========================================
        planos = [
            ("Mensal", 0.0, 1),
            ("Trimestral", 0.05, 3),
            ("Semestral", 0.10, 6),
            ("Anual", 0.15, 12),
            ("Misto (2+ Turmas)", 0.10, 1) # Desconto global para quem faz mais de uma modalidade
        ]
        cursor.executemany('INSERT INTO planos (nome_plano, percentual_desconto, duracao_meses) VALUES (?, ?, ?)', planos)

        # ==========================================
        # 3. TURMAS
        # ==========================================
        turmas = [
            ("Jazz Adulto Iniciante", 1, "Sala Grande", "19:30", "21:00", "Terça, Quinta", 150.00, "Parceiro", 0, None, None),
            ("Hip Hop Teen", 2, "Sala Pequena", "18:00", "19:00", "Segunda, Quarta", 120.00, "Propria", 0, None, None),
            ("Ballet Infantil", 3, "Sala Grande", "09:00", "10:30", "Sábado", 140.00, "Propria", 0, None, None),
            ("Contemporâneo Avançado", 4, "Sala Grande", "20:00", "21:30", "Segunda, Quarta", 160.00, "Parceiro", 0, None, None),
            ("Particular - Dança dos Noivos", 1, "Dinâmica", "", "", "", None, "Parceiro", 1, '[{"dia":"Sábado","sala":"Sala Pequena","inicio":"11:00","fim":"12:00"}]', 80.00)
        ]
        cursor.executemany('''
            INSERT INTO turmas (nome_turma, id_professor, sala, hora_inicio, hora_fim, dias_semana, valor_mensal_base, tipo_gestao, is_particular, cronograma, valor_por_aula) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', turmas)

        # ==========================================
        # 4. ALUNOS
        # ==========================================
        alunos = [
            ("Carlos Silva", "111.111.111-11", "11911111111", "carlos@email.com", "1990-05-14"),
            ("Mariana Oliveira", "222.222.222-22", "11922222222", "mariana@email.com", "1995-08-20"),
            ("João Pedro", "333.333.333-33", "11933333333", "joao@email.com", "2005-02-10"),
            ("Beatriz Souza", "444.444.444-44", "11944444444", "bia@email.com", "2010-11-25"),
            ("Fernanda Lima", "555.555.555-55", "11955555555", "fernanda@email.com", "1988-03-30"),
            ("Lucas Mendes", "666.666.666-66", "11966666666", "lucas@email.com", "1992-07-12"),
            ("Amanda Costa", "777.777.777-77", "11977777777", "amanda@email.com", "1999-12-05"),
            ("Diego Alves", "888.888.888-88", "11988888888", "diego@email.com", "1985-09-18"),
            ("Camila Rocha", "999.999.999-99", "11999999999", "camila@email.com", "2001-04-22"),
            ("Bruno Carvalho", "000.000.000-00", "11900000000", "bruno@email.com", "1996-01-08")
        ]
        cursor.executemany('INSERT INTO alunos (nome, cpf, contato_1, email, data_nascimento) VALUES (?, ?, ?, ?, ?)', alunos)

        # ==========================================
        # 5. INSCRIÇÕES (Matrículas Ativas)
        # ==========================================
        # O Carlos faz Jazz (Turma 1) e Hip Hop (Turma 2) -> Exemplo perfeito para o Plano Misto!
        inscricoes = [
            (1, 1, "01/04/2026", "Pago"), (1, 2, "01/04/2026", "Pago"), # Carlos
            (2, 4, "01/04/2026", "Pago"), # Mariana
            (3, 2, "05/04/2026", "Pendente"), # João (Matrícula Pendente)
            (4, 3, "10/04/2026", "Pago"), # Beatriz
            (5, 1, "15/04/2026", "Pago"), # Fernanda
            (6, 5, "20/04/2026", "Pago")  # Lucas (Particular Noivos)
        ]
        cursor.executemany('INSERT INTO inscricoes (id_aluno, id_turma, data_inscricao, status_pagamento_matricula) VALUES (?, ?, ?, ?)', inscricoes)

        # Atualizando o Caixa Matrículas (5 matrículas pagas x R$ 100 = 500)
        cursor.execute('UPDATE saldos_caixa SET saldo_matriculas = 500.00 WHERE id_saldo = 1')

        # ==========================================
        # 6. FATURAS & PAGAMENTOS (A Mágica do Header/Detail)
        # ==========================================
        # Fatura 1: Carlos (Mês 04/2026) - Faz 2 turmas (150 + 120 = 270), ganha 10% (Plano Misto) -> Paga 243.
        cursor.execute("INSERT INTO faturas (id_aluno, mes_referencia, data_vencimento, valor_bruto, desconto_aplicado, valor_final, status) VALUES (1, '04/2026', '10/04/2026', 270.00, 27.00, 243.00, 'Pago')")
        id_fatura_carlos = cursor.lastrowid
        cursor.execute("INSERT INTO pagamentos (id_fatura, id_aluno, id_turma, id_plano, mes_referencia, data_vencimento, valor_final, status) VALUES (?, 1, 1, 5, '04/2026', '10/04/2026', 135.00, 'Pago')", (id_fatura_carlos,))
        cursor.execute("INSERT INTO pagamentos (id_fatura, id_aluno, id_turma, id_plano, mes_referencia, data_vencimento, valor_final, status) VALUES (?, 1, 2, 5, '04/2026', '10/04/2026', 108.00, 'Pago')", (id_fatura_carlos,))

        # Fatura 2: Mariana (Mês 04/2026) - Contemporâneo (160), Plano Mensal. (Fatura Pendente)
        cursor.execute("INSERT INTO faturas (id_aluno, mes_referencia, data_vencimento, valor_bruto, desconto_aplicado, valor_final, status) VALUES (2, '04/2026', '10/04/2026', 160.00, 0.00, 160.00, 'Pendente')")
        id_fatura_mariana = cursor.lastrowid
        cursor.execute("INSERT INTO pagamentos (id_fatura, id_aluno, id_turma, id_plano, mes_referencia, data_vencimento, valor_final, status) VALUES (?, 2, 4, 1, '04/2026', '10/04/2026', 160.00, 'Pendente')", (id_fatura_mariana,))

        # Fatura 3: João (Mês 04/2026) - Hip Hop (120), Plano Trimestral (5%). (Fatura Vencida simulada)
        cursor.execute("INSERT INTO faturas (id_aluno, mes_referencia, data_vencimento, valor_bruto, desconto_aplicado, valor_final, status) VALUES (3, '04/2026', '05/04/2026', 120.00, 6.00, 114.00, 'Vencido')")
        id_fatura_joao = cursor.lastrowid
        cursor.execute("INSERT INTO pagamentos (id_fatura, id_aluno, id_turma, id_plano, mes_referencia, data_vencimento, valor_final, status) VALUES (?, 3, 2, 2, '04/2026', '05/04/2026', 114.00, 'Pendente')", (id_fatura_joao,))

        # Adicionando o pagamento do Carlos no Caixa Principal
        cursor.execute('UPDATE saldos_caixa SET saldo_principal = 243.00 WHERE id_saldo = 1')

        # ==========================================
        # 7. DESPESAS
        # ==========================================
        despesas = [
            ("Aluguel do Espaço", "Fixa", 2500.00, "2026-04-05", "04/2026", "Pendente"),
            ("Conta de Luz", "Variável", 320.50, "2026-04-12", "04/2026", "Pendente"),
            ("Internet", "Fixa", 99.90, "2026-04-15", "04/2026", "Pendente")
        ]
        cursor.executemany("INSERT INTO despesas (descricao, tipo_despesa, valor, data_vencimento, mes_referencia, status_pagamento) VALUES (?, ?, ?, ?, ?, ?)", despesas)

        # ==========================================
        # 8. EVENTOS E FINANCEIRO DE EVENTOS
        # ==========================================
        eventos = [
            ("Festival de Inverno 2026", "2026-07-20"),
            ("Mostra de Dança Infantil", "2026-10-12")
        ]
        cursor.executemany("INSERT INTO eventos (nome_evento, data_evento) VALUES (?, ?)", eventos)

        transacoes_eventos = [
            # Transações do Evento 1 (Festival de Inverno)
            (1, "Patrocínio Empresa Local", "Entrada", 1500.00),
            (1, "Venda de Ingressos (Lote 1)", "Entrada", 3500.00),
            (1, "Aluguel do Teatro", "Saida", 2000.00),
            (1, "Figurinos e Cenário", "Saida", 1200.00),
            
            # Transações do Evento 2 (Mostra Infantil)
            (2, "Venda de Ingressos", "Entrada", 2000.00),
            (2, "Decoração e Iluminação", "Saida", 600.00)
        ]
        cursor.executemany('''
            INSERT INTO financeiro_eventos (id_evento, descricao, tipo, valor) 
            VALUES (?, ?, ?, ?)
        ''', transacoes_eventos)

        cursor.execute('UPDATE saldos_caixa SET saldo_eventos = 3200.00 WHERE id_saldo = 1')

        conexao.commit()
        print("✅ Banco de dados populado com sucesso! A despensa está cheia de dados reais.")

    except Exception as e:
        print(f"❌ Ocorreu um erro ao popular o banco: {e}")
        conexao.rollback()
    finally:
        conexao.close()

if __name__ == '__main__':
    popular_banco_seed()