# PROJETO: GESTÃO ESCOLA DE DANÇA
# OBJETIVO: Sistema de gestão de alunos, turmas e financeiro.

# ESTRUTURA DE DADOS PLANEJADA:
# - Alunos: id, nome, cpf, rg, endereco, email, contato, responsavel, data de nascimento
# - Turmas: id, nome_turma, professor, horario, dias_semana, id_plano
# - Planos: id, nome_plano, valor_base
# - Tipos_Desconto: id, nome_desconto, percentual
# - Pagamentos: id, id_aluno, id_plano, id_desconto, data_vencimento, status

class Aluno:
    def __init__(self, id_aluno, nome, cpf, rg, endereco, data_nascimento, email, contato, responsavel):
        self.id_aluno = id_aluno
        self.nome = nome
        self.cpf = cpf
        self.rg = rg
        self.endereco = endereco
        self.data_nascimento = data_nascimento
        self.email = email
        self.contato = contato
        self.responsavel = responsavel
        self.turmas = []  # Lista para armazenar as turmas em que o aluno está matriculado
        self.plano = []  # Atributo para armazenar o plano do aluno

    def adicionar_turma(self, turma):
        self.turmas.append(turma)
        print(f"Aluno {self.nome} matriculado na turma {turma}!")

class Plano:
    def __init__(self, id_plano, nome_plano, valor_base):
        self.id_plano = id_plano
        self.nome_plano = nome_plano
        self.valor_base = valor_base

class Turma:
    def __init__(self, id_turma, nome_turma, professor, horario, dias_semana, valor_mensal_base):
        self.id_turma = id_turma
        self.nome_turma = nome_turma
        self.professor = professor
        self.horario = horario
        self.dias_semana = dias_semana
        self.valor_mensal_base = valor_mensal_base

from datetime import datetime

class Pagamento:
    def __init__(self, id_pagamento, aluno, turma, plano_contratado, mes_referencia, data_vencimento):
        self.id_pagamento = id_pagamento
        self.aluno = aluno
        self.turma = turma  
        self.plano_contratado = plano_contratado
        self.mes_referencia = mes_referencia
        self.data_vencimento = datetime.strptime(data_vencimento, "%d/%m/%Y")
        self.valor_final = 0.0
        self.status = "Pendente"

    def calcular_pagamento(self, data_pagamento_str):
        data_pagamento = datetime.strptime(data_pagamento_str, "%d/%m/%Y")
        
        # O valor base da turma é sempre o valor do plano "Mensal"
        valor_base = self.turma.valor_mensal_base 

        if data_pagamento > self.data_vencimento:
            # REGRA: Perde o desconto do plano e paga Valor Base + 10%
            self.valor_final = valor_base * 1.10
            print(f"Atenção: Pagamento em atraso!")
            print(f"O desconto do plano '{self.plano_contratado.nome_plano}' foi perdido.")
            print(f"Valor calculado sobre a base (R$ {valor_base:.2f}) + 10% de multa.")
        else:
            # REGRA: Pagamento em dia, mantém o valor do plano contratado
            self.valor_final = self.plano_contratado.valor_base
            print(f"Pagamento em dia! Valor do plano '{self.plano_contratado.nome_plano}' aplicado.")

        self.status = "Pago"
        print(f"Valor Final: R$ {self.valor_final:.2f}")

