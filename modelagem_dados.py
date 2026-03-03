# PROJETO: GESTÃO ESCOLA DE DANÇA
# OBJETIVO: Sistema de gestão de alunos, turmas e financeiro.

# ESTRUTURA DE DADOS PLANEJADA:
# - Alunos: id_aluno, nome, cpf, rg, endereco, data_nascimento, email, contato, responsavel
# - Turmas: id_turma, nome_turma, professor, horario, dias_semana, valor_mensal_base
# - Planos: id_plano, nome_plano, percentual_desconto
# - Pagamentos: id_pagamento, aluno, turma, plano_contratado, mes_referencia, data_vencimento

from datetime import datetime

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
        self.turmas = []  
        self.plano_atual = None

    def __repr__(self):
        return f"Aluno({self.nome})"

    def adicionar_turma(self, turma):
        self.turmas.append(turma)
        print(f"Aluno {self.nome} matriculado na turma {turma.nome_turma}!")

class Plano:
    def __init__(self, id_plano, nome_plano, percentual_desconto):
        self.id_plano = id_plano
        self.nome_plano = nome_plano
        self.percentual_desconto = percentual_desconto

class Turma:
    def __init__(self, id_turma, nome_turma, professor, horario, dias_semana, valor_mensal_base):
        self.id_turma = id_turma
        self.nome_turma = nome_turma
        self.professor = professor
        self.horario = horario
        self.dias_semana = dias_semana
        self.valor_mensal_base = valor_mensal_base

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
        
        # Valor cheio da turma específica (pode ser 125, 150, etc.)
        valor_cheio = self.turma.valor_mensal_base 

        # LÓGICA DO PLANO MISTO
        # Se for Misto e tiver + de 1 turma, aplica o desconto do plano.
        # Se for outro plano (Trimestral/Semestral), também aplica o respectivo percentual.
        if self.plano_contratado.nome_plano == "Misto" and len(self.aluno.turmas) <= 1:
            # Caso o plano seja Misto mas o aluno só tenha 1 turma, ele paga o valor cheio
            valor_com_desconto = valor_cheio
            msg_plano = "Plano Misto não aplicado (apenas 1 turma ativa)"
        else:
            desconto = valor_cheio * self.plano_contratado.percentual_desconto
            valor_com_desconto = valor_cheio - desconto
            msg_plano = f"Plano {self.plano_contratado.nome_plano} aplicado"

        if data_pagamento > self.data_vencimento:
            # REGRA DE OURO: Atrasou? Base da Turma + 10%
            self.valor_final = valor_cheio * 1.10
            status_msg = f"ATRASO: Base R$ {valor_cheio:.2f} + 10% multa"
        else:
            self.valor_final = valor_com_desconto
            status_msg = f"EM DIA: {msg_plano}"

        self.status = "Pago"
        print(f"[{self.mes_referencia}] {status_msg} | Total: R$ {self.valor_final:.2f}")
