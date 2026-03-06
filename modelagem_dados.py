# PROJETO: GESTÃO ESCOLA DE DANÇA
# OBJETIVO: Sistema de gestão de alunos, turmas e financeiro (ERP).

# ESTRUTURA DE DADOS PLANEJADA:
# - Alunos: id_aluno, nome, cpf, rg, endereco, data_nascimento, email, contato, responsavel
# - Professores: id_professor, nome, telefone, chave_pix
# - Turmas: id_turma, nome_turma, professor, horario, dias_semana, valor_mensal_base, tipo_gestao
# - Planos: id_plano, nome_plano, percentual_desconto
# - Pagamentos: id_pagamento, aluno, turma, plano_contratado, mes_referencia, data_vencimento
# - Eventos: id_evento, nome_evento, receitas, despesas
# - GestorFinanceiro: mes_referencia, pagamentos, despesas_fixas, eventos

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

class Professor:
    def __init__(self, id_professor, nome, telefone, chave_pix):
        self.id_professor = id_professor
        self.nome = nome
        self.telefone = telefone
        self.chave_pix = chave_pix

    def __repr__(self):
        return f"Professor({self.nome})"

class Turma:
    def __init__(self, id_turma, nome_turma, professor, horario, dias_semana, valor_mensal_base, tipo_gestao="Propria"):
        self.id_turma = id_turma
        self.nome_turma = nome_turma
        self.professor = professor
        self.horario = horario
        self.dias_semana = dias_semana
        self.valor_mensal_base = valor_mensal_base
        self.tipo_gestao = tipo_gestao

# Função para calcular o repasse para o professor parceiro, caso a turma seja do tipo "Parceiro"
    def calcular_repasse(self, valor_pago):
        if self.tipo_gestao == "Parceiro":
            return valor_pago * 0.75  # 75% do valor vai para o professor parceiro
        return 0.0  # Turma própria não tem repasse de locação

class Pagamento:
    def __init__(self, id_pagamento, aluno, turma, plano_contratado, mes_referencia, data_vencimento, 
                 desconto_manual=0.0, taxa_maquininha=0.0):
        self.id_pagamento = id_pagamento
        self.aluno = aluno
        self.turma = turma  
        self.plano_contratado = plano_contratado
        self.mes_referencia = mes_referencia
        self.data_vencimento = datetime.strptime(data_vencimento, "%d/%m/%Y")
        
        # NOVOS CAMPOS
        self.desconto_manual = desconto_manual  # Para bolsistas ou acordos
        self.taxa_maquininha = taxa_maquininha  # Valor em R$ que a maquininha cobra
        
        self.valor_final = 0.0
        self.valor_repasse = 0.0
        self.valor_liquido_escola = 0.0
        self.status = "Pendente"

    def calcular_pagamento(self, data_pagamento_str):
        data_pagamento = datetime.strptime(data_pagamento_str, "%d/%m/%Y")
        valor_cheio = self.turma.valor_mensal_base 

        # Lógica de planos (Misto vs Outros)
        if self.plano_contratado.nome_plano == "Misto" and len(self.aluno.turmas) <= 1:
            valor_base_com_plano = valor_cheio
        else:
            desconto_plano = valor_cheio * self.plano_contratado.percentual_desconto
            valor_base_com_plano = valor_cheio - desconto_plano

        # Aplica o desconto manual (Bolsa/Condição especial)
        valor_com_descontos = valor_base_com_plano - self.desconto_manual

        if data_pagamento > self.data_vencimento:
            # Multa de 10% sobre o valor cheio da turma
            self.valor_final = valor_cheio * 1.10
        else:
            self.valor_final = valor_com_descontos

        # IMPORTANTE: A taxa da maquininha é uma despesa da escola, 
        # então ela diminui o que sobra para a escola, mas não o que o aluno paga.
        self.status = "Pago"
        
        self.valor_repasse = self.turma.calcular_repasse(self.valor_final)
        # O líquido da escola agora desconta a taxa da maquininha também!
        self.valor_liquido_escola = self.valor_final - self.valor_repasse - self.taxa_maquininha

class Evento:
    def __init__ (self, id_evento, nome_evento, receitas=0.0, despesas=0.0):
        self.id_evento = id_evento
        self.nome_evento = nome_evento
        self.receitas = receitas
        self.despesas = despesas

    def saldo(self):
        return self.receitas - self.despesas
    
class GestorFinanceiro:
    def __init__(self, mes_referencia, retencao_caixa, saldo_anterior=0.0):
        self.mes_referencia = mes_referencia
        self.retencao_caixa = retencao_caixa
        self.saldo_anterior = saldo_anterior 
        self.pagamentos = []
        self.eventos = []
        self.despesas_fixas = 0.0
        self.extras = [] 

    def adicionar_pagamento(self, pagamento):
        if pagamento.status == "Pago":
            self.pagamentos.append(pagamento)

    # NOVO MÉTODO: Para registrar coisas que não são mensalidades nem eventos
    def adicionar_extra(self, descricao, valor):
        self.extras.append((descricao, valor))

    def fechar_mes(self):
        print(f"\n{'='*15} FECHAMENTO CAIXA: {self.mes_referencia} {'='*15}")
        
        # 1. RELATÓRIO DE REPASSES (Professores Parceiros)
        print("\n--- REPASSES PARA PROFESSORES PARCEIROS ---")
        repasses = {} 
        
        for p in self.pagamentos:
            if p.turma.tipo_gestao == "Parceiro":
                prof = p.turma.professor 
                
                if prof not in repasses:
                    repasses[prof] = 0.0
                
                repasses[prof] += p.valor_repasse
        
        if repasses:
            for prof, valor in repasses.items():
                print(f"Transferir para {prof.nome} | PIX: {prof.chave_pix} | Valor: R$ {valor:.2f}")
        else:
            print("Nenhum repasse a ser feito neste mês.")

        # 2. BALANÇO OPERACIONAL E EXTRAS
        print("\n--- BALANÇO OPERACIONAL (MENSALIDADES E EXTRAS) ---")
        receita_turmas_liquida = sum(p.valor_liquido_escola for p in self.pagamentos)
        print(f"Receita Líquida Turmas (Escola): R$ {receita_turmas_liquida:.2f}")
        
        # PROCESSANDO OS EXTRAS
        total_extras = 0.0
        if self.extras:
            print("\n  >> Detalhamento de Extras:")
            for descricao, valor in self.extras:
                # Cria um sinal de "+" visual para facilitar a leitura se for lucro
                sinal = "+" if valor > 0 else ""
                print(f"     {descricao}: {sinal}R$ {valor:.2f}")
            
            # Soma todos os valores da posição [1] das tuplas
            total_extras = sum(valor for descricao, valor in self.extras)
            print(f"  >> Resultado dos Extras: R$ {total_extras:.2f}\n")

        # O lucro operacional agora abraça os extras também!
        lucro_operacional = receita_turmas_liquida - self.despesas_fixas + total_extras
        print(f"Despesas Fixas da Escola: R$ {self.despesas_fixas:.2f}")
        print(f"Lucro Operacional: R$ {lucro_operacional:.2f}")

        # 3. DIVISÃO SOCIETÁRIA
        print("\n--- DIVISÃO DE LUCROS (SÓCIAS) ---")
        valor_distribuir = lucro_operacional - self.retencao_caixa

        if valor_distribuir > 0:
            salario_socias = valor_distribuir / 2
            print(f"Retenção Mensal para o Caixa: R$ {self.retencao_caixa:.2f}")
            print(f"Repasse Sócia 1: R$ {salario_socias:.2f}")
            print(f"Repasse Sócia 2: R$ {salario_socias:.2f}")
        else:
            print("Atenção: Saldo insuficiente para divisão após descontar despesas e retenção.")

        # 4. CAIXA GERAL DA ESCOLA
        print("\n--- CAIXA GERAL DA ESCOLA ---")
        saldo_eventos = sum(e.saldo() for e in self.eventos)
        print(f"Resultado de Eventos no Mês: R$ {saldo_eventos:.2f}")
        
        movimentacao_caixa = self.saldo_anterior + self.retencao_caixa + saldo_eventos
        
        if movimentacao_caixa >= 0:
            print(f"Valor a ser guardado no Caixa da Escola: R$ {movimentacao_caixa:.2f}")
        else:
            print(f"ATENÇÃO: Eventos deram déficit. Retirar do Caixa: R$ {abs(movimentacao_caixa):.2f}")
            
        print("="*50)

