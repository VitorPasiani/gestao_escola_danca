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

import calendar

class Aluno:
    def __init__(self, id_aluno, nome, cpf, rg, endereco, data_nascimento, email, contato_1, contato_2, responsavel, ativo=1):
        self.id_aluno = id_aluno
        self.nome = nome
        self.cpf = cpf
        self.rg = rg
        self.endereco = endereco
        self.data_nascimento = data_nascimento
        self.email = email
        self.contato_1 = contato_1
        self.contato_2 = contato_2
        self.responsavel = responsavel
        self.ativo = ativo
        self.turmas = []  
        self.plano_atual = None

    def __repr__(self):
        return f"Aluno({self.nome})"

    def adicionar_turma(self, turma):
        self.turmas.append(turma)
        print(f"Aluno {self.nome} matriculado na turma {turma.nome_turma}!")

class Plano:
    def __init__(self, id_plano, nome_plano, percentual_desconto, duracao_meses=1):
        self.id_plano = id_plano
        self.nome_plano = nome_plano
        self.percentual_desconto = percentual_desconto
        self.duracao_meses = duracao_meses

class Professor:
    def __init__(self, id_professor, nome, telefone, chave_pix, ativo=1):
        self.id_professor = id_professor
        self.nome = nome
        self.telefone = telefone
        self.chave_pix = chave_pix
        self.ativo = ativo

    def __repr__(self):
        return f"Professor({self.nome})"

class Turma:
    def __init__(self, id_turma, nome_turma, professor, horario, dias_semana, valor_mensal_base, tipo_gestao="Propria", ativo=1):
        self.id_turma = id_turma
        self.nome_turma = nome_turma
        self.professor = professor
        self.horario = horario
        self.dias_semana = dias_semana
        self.valor_mensal_base = valor_mensal_base
        self.tipo_gestao = tipo_gestao
        self.ativo = ativo

    # Essa função pertence à Turma normal!
    def calcular_repasse(self, valor_pago):
        if self.tipo_gestao == "Parceiro":
            return valor_pago * 0.75  # 75% do valor vai para o professor parceiro
        return 0.0  # Turma própria não tem repasse de locação

class TurmaParticular:
    def __init__(self, id_turma, aluno_nome, professor, cronograma, valor_por_aula=40.00, percentual_repasse=0.75):
        self.id_turma = id_turma
        self.nome_turma = f"Particular - {aluno_nome}"
        self.professor = professor
        self.cronograma = cronograma 
        self.valor_por_aula = valor_por_aula
        self.percentual_repasse = percentual_repasse
        self.tipo_gestao = "Parceiro"

    def calcular_repasse(self, valor_pago):
        return valor_pago * self.percentual_repasse

    def calcular_aulas_no_mes(self, ano, mes):
        mapa_dias = {
            "Segunda": 0, "Terça": 1, "Quarta": 2, "Quinta": 3, 
            "Sexta": 4, "Sábado": 5, "Domingo": 6
        }
        total_aulas = 0
        calendario_mes = calendar.monthcalendar(ano, mes)
        
        for semana in calendario_mes:
            for nome_dia, qtd_aulas in self.cronograma.items():
                numero_do_dia = mapa_dias.get(nome_dia)
                if numero_do_dia is not None and semana[numero_do_dia] != 0:
                    total_aulas += qtd_aulas
                    
        return total_aulas
   
class AulaAvulsa:
    def __init__(self, aluno_nome, professor, data_aula, valor_total_aula_avulsa, percentual_repasse=0.0):
        self.aluno_nome = aluno_nome
        self.professor = professor
        self.data_aula = data_aula
        self.valor_total_aula_avulsa = valor_total_aula_avulsa
        
        self.repasse_prof = self.valor_total_aula_avulsa * percentual_repasse # Exemplo: 0.75 para 75% de repasse
        self.lucro_caixa_avulso = self.valor_total_aula_avulsa - self.repasse_prof

class Pagamento:
    def __init__(self, id_pagamento, aluno, turma, plano_contratado, mes_referencia, data_vencimento, 
                 data_pagamento=None, desconto_manual=0.0, tipo_desconto_manual="R$", taxa_maquininha=0.0):
        
        self.id_pagamento = id_pagamento
        self.aluno = aluno
        self.turma = turma  
        self.plano_contratado = plano_contratado
        self.mes_referencia = mes_referencia
        self.data_vencimento = datetime.strptime(data_vencimento, "%d/%m/%Y")
        self.data_pagamento = data_pagamento
        
        self.desconto_manual = desconto_manual  # Para bolsistas ou acordos (R$)
        self.tipo_desconto_manual = tipo_desconto_manual  # Pode ser "R$" ou "%"
        self.taxa_maquininha = taxa_maquininha  # Porcentagem da maquininha (ex: 0.03)
        
        self.valor_final = 0.0
        self.valor_repasse = 0.0
        self.valor_liquido_escola = 0.0
        self.status = "Pendente" if not data_pagamento else "Pago"

    def calcular_pagamento(self, data_pagamento_str):
        self.data_pagamento = data_pagamento_str
        
        # Converte a string para data para fazer a matemática de atraso
        data_pag_dt = datetime.strptime(data_pagamento_str, "%d/%m/%Y")
        
        # =======================================================
        # 1. TURMA PARTICULAR/TURMA NORMAL
        # =======================================================
        if self.turma.tipo_gestao == "Particular": 
            ano = self.data_vencimento.year
            mes = self.data_vencimento.month
            qtd_aulas = self.turma.calcular_aulas_no_mes(ano, mes)
            valor_cheio = self.turma.valor_por_aula * qtd_aulas
            print(f"[Sistema] {qtd_aulas} aulas calculadas para {self.turma.nome_turma} em {mes:02d}/{ano}.")
        else:
            valor_cheio = self.turma.valor_mensal_base 

        # =======================================================
        # 2. LÓGICA DE PLANOS E DESCONTOS (Regra do Bolsista)
        # =======================================================
        # VERIFICA SE É BOLSISTA (Tem desconto manual?)
        if self.desconto_manual > 0:
            if self.tipo_desconto_manual == "%": # Se for porcentagem, calcula o valor a ser abatido com base no valor cheio da mensalidade
                valor_abatido = valor_cheio * self.desconto_manual
                valor_com_todos_descontos = valor_cheio - valor_abatido
            else:
                # Exemplo: desconto_manual = 50.00 (Desconto fixo de R$ 50,00)
                valor_com_todos_descontos = valor_cheio - self.desconto_manual

        else:
            # SE NÃO É BOLSISTA, SEGUE A REGRA DOS PLANOS
            if self.plano_contratado and self.plano_contratado.nome_plano == "Misto" and len(self.aluno.turmas) <= 1:
                valor_com_todos_descontos = valor_cheio
            elif self.plano_contratado:
                desconto_plano = valor_cheio * self.plano_contratado.percentual_desconto
                valor_com_todos_descontos = valor_cheio - desconto_plano
            else:
                valor_com_todos_descontos = valor_cheio

        # REGRA DO ATRASO
        if data_pag_dt > self.data_vencimento:
            self.valor_final = valor_cheio * 1.10
        else:
            self.valor_final = valor_com_todos_descontos

        # =======================================================
        # 3. DISTRIBUIÇÃO DO DINHEIRO E TAXAS
        # =======================================================
        self.status = "Pago"
        
        # Calcula o repasse (se houver)
        self.valor_repasse = self.turma.calcular_repasse(self.valor_final) if hasattr(self.turma, 'calcular_repasse') else 0.0        
        
        # Calcula quanto a maquininha levou (Porcentagem em cima do que o aluno pagou)
        desconto_banco = self.valor_final * self.taxa_maquininha
        
        # O líquido da escola é o que sobra tirando o professor e o banco
        self.valor_liquido_escola = self.valor_final - self.valor_repasse - desconto_banco

class Evento:
    def __init__ (self, id_evento, nome_evento, data_evento=None):
        self.id_evento = id_evento
        self.nome_evento = nome_evento
        self.data_evento = data_evento

        self.transacoes = []  # Lista de tuplas (descricao, valor) para registrar receitas e despesas do evento

    def adicionar_transacao(self, descricao, tipo, valor):
        self.transacoes.append({"descricao": descricao, "tipo": tipo, "valor": valor})

    def saldo(self):
        total_entradas = sum(t["valor"] for t in self.transacoes if t["tipo"] == "Entrada") #Soma apenas as transações do tipo "Entrada"
        total_saidas = sum(t["valor"] for t in self.transacoes if t["tipo"] == "Saída") #Soma apenas as transações do tipo "Saída"
        return total_entradas - total_saidas # Retorna o saldo final do evento (positivo ou negativo)
    
class GestorFinanceiro:
    def __init__(self, mes_referencia, retencao_caixa, saldo_principal=0.0, saldo_matriculas=0.0, saldo_avulsas=0.0):
        self.mes_referencia = mes_referencia
        self.retencao_caixa = retencao_caixa
        self.aulas_avulsas = []

        # Saldos dos 3 caixas para controle interno (não afetam o fechamento, mas ajudam a organizar as contas)
        self.saldo_principal = saldo_principal
        self.saldo_matriculas = saldo_matriculas
        self.saldo_avulsas = saldo_avulsas

        # HISTÓRICO DE SAQUES (Para saber com o que o dinheiro foi gasto)
        self.historico_retiradas = {
            "Principal": [],
            "Matriculas": [],
            "Avulsas": []
        }

        self.pagamentos = []
        self.eventos = []
        self.despesas_fixas = 0.0
        self.extras = [] 

    # Método para registrar matrículas, adicionando o valor da matrícula ao caixa de matrículas
    def registrar_matricula(self, aluno, valor=100.00):
        self.saldo_matriculas += valor
        print(f"Matrícula de {aluno.nome} registrada! +R$ {valor:.2f} no Caixa Matrículas.")

    # Método para registrar aulas avulsas, adicionando o lucro da escola ao caixa de avulsas
    def registrar_aula_avulsa(self, aula_avulsa):
        self.aulas_avulsas.append(aula_avulsa)
    
        self.saldo_avulsas += aula_avulsa.lucro_caixa_avulso
        print(f"Aula Avulsa de {aula_avulsa.aluno_nome} registrada! +R${aula_avulsa.lucro_caixa_avulso:.2f} no Caixa Avulsas.")

    # Método para registrar saques do caixa, com descrição do motivo
    def retirar_caixa_matriculas(self, valor, descricao):
        if self.saldo_matriculas >= valor: # Verifica se há saldo suficiente antes de retirar
            self.saldo_matriculas -= valor # Se sim, retira o valor do caixa de matrículas
            # Anota no histórico o que foi comprado e quanto custou
            self.historico_retiradas["Matriculas"].append((descricao, valor))
            print(f"Saque [Matrículas]: -R$ {valor:.2f} ({descricao}). Saldo: R$ {self.saldo_matriculas:.2f}")
        else:
            print(f"Erro: Saldo insuficiente no Caixa Matrículas para comprar '{descricao}'.") # Caso tente retirar mais do que o saldo disponível, exibe uma mensagem de erro.

    def retirar_caixa_avulsas(self, valor, descricao):
        if self.saldo_avulsas >= valor:
            self.saldo_avulsas -= valor
            self.historico_retiradas["Avulsas"].append((descricao, valor))
            print(f"Saque [Avulsas]: -R$ {valor:.2f} ({descricao}). Saldo: R$ {self.saldo_avulsas:.2f}")
        else:
            print(f"Erro: Saldo insuficiente no Caixa Avulsas para '{descricao}'.")

    def retirar_caixa_principal(self, valor, descricao):
        if self.saldo_principal >= valor:
            self.saldo_principal -= valor
            self.historico_retiradas["Principal"].append((descricao, valor))
            print(f"Saque [Principal]: -R$ {valor:.2f} ({descricao}). Saldo: R$ {self.saldo_principal:.2f}")
        else:
            print(f"Erro: Saldo insuficiente no Caixa Principal para '{descricao}'.")

    def adicionar_pagamento(self, pagamento):
        if pagamento.status == "Pago":
            self.pagamentos.append(pagamento)

    # Registrar movimentações que não são mensalidades nem eventos
    def adicionar_extra(self, descricao, valor):
        self.extras.append((descricao, valor))

    def fechar_mes(self):
        # 1. Formulário de fechamento mensal
        relatorio = {
            "mes_referencia": self.mes_referencia,
            "repasses_professores": [],
            "receita_turmas_liquida": 0.0,
            "total_extras": 0.0,
            "despesas_fixas": 0.0,
            "lucro_operacional": 0.0,
            "retencao_caixa": 0.0,
            "repasse_socias": 0.0,
            "saldo_eventos": 0.0,
            "movimentacao_caixa_geral": 0.0
        }

        # 2. Lógica dos Repasses dos Professores
        repasses = {} 
        for p in self.pagamentos:
            if p.turma.tipo_gestao == "Parceiro":
                prof = p.turma.professor 
                if prof not in repasses:
                    repasses[prof] = 0.0
                repasses[prof] += p.valor_repasse

        for avulsa in self.aulas_avulsas:
            prof = avulsa.professor
            if prof not in repasses:
                repasses[prof] = 0.0
            repasses[prof] += avulsa.repasse_prof
        
        if repasses:
            for prof, valor in repasses.items():
                relatorio["repasses_professores"].append({
                    "nome_professor": prof.nome,
                    "chave_pix": prof.chave_pix,
                    "valor_repasse": valor
                })

        # 3. Balanço Operacional e Extras
        receita_turmas = sum(p.valor_liquido_escola for p in self.pagamentos)
        relatorio["receita_turmas_liquida"] = receita_turmas

        total_extras = sum(valor for _, valor in self.extras)
        relatorio["total_extras"] = total_extras

        lucro_op = receita_turmas - self.despesas_fixas + total_extras
        relatorio["lucro_operacional"] = lucro_op
        relatorio["despesas_fixas"] = self.despesas_fixas

        # 4. Divisão Societária
        valor_distribuir = lucro_op - self.retencao_caixa
        if valor_distribuir > 0:
            relatorio["repasse_socias"] = valor_distribuir / 2
        else:
            relatorio["repasse_socias"] = 0.0
            
        relatorio["retencao_caixa"] = self.retencao_caixa

        # 5. Eventos e Caixa Geral
        saldo_eventos = 0.0
        for e in self.eventos:
            saldo_eventos += e.saldo()
            
        relatorio["saldo_eventos"] = saldo_eventos

        movimentacao_caixa = self.saldo_principal + self.retencao_caixa + saldo_eventos
        relatorio["movimentacao_caixa_geral"] = movimentacao_caixa

        return relatorio
