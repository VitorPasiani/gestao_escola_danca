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

novo_aluno = Aluno(1, "Pasi", "123.456.789-00", "00.000.000-0", "Rua aaaaaa, nº aaaa, bairro aaaa, aaa/aa", "aaaaaa@aaaa.com", "(00) 00000-0000", "N/A", "01/01/2000")

print(f"Aluno criado: {novo_aluno.nome}")