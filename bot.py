import os
import csv
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Carregar variáveis de ambiente
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

CSV_FILE = "dados.csv"

# Definir as faturas com seus limites
faturas = [
    {"nome": "Itau", "vencimento": 7, "limite": 1300, "gasto": 0},
    {"nome": "Inter", "vencimento": 7, "limite": 250, "gasto": 0},
    {"nome": "Nubank", "vencimento": 7, "limite": 200, "gasto": 0}
]

# Definir os salários
salarios = [1400, 560, 840]  # valores fixos que você mencionou
saldo_conta = sum(salarios)  # Calcula o saldo total da conta

# Função para registrar gastos e recebimentos
def registrar(tipo, valor, categoria, descricao, metodo):
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), tipo, valor, categoria, descricao, metodo])

# Função para registrar o gasto e atualizar o limite
async def gastar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global saldo_conta  # Atualiza o saldo global da conta
    try:
        valor = float(context.args[0])
        categoria = context.args[1]
        descricao = " ".join(context.args[2:-1])
        metodo = context.args[-1]

        # Atualizar o valor do gasto para o cartão correspondente
        for fatura in faturas:
            if fatura["nome"].lower() == metodo.lower():
                fatura["gasto"] += valor
                break

        # Se o método for 'Pix', desconta da conta
        if metodo.lower() == "pix":
            saldo_conta -= valor  # Diminui o valor da conta

        # Registrar o gasto
        registrar("gasto", valor, categoria, descricao, metodo)

        # Resposta
        await update.message.reply_text(f"Gasto de R${valor:.2f} registrado em '{categoria}' via {metodo}.")

    except Exception as e:
        print(e)
        await update.message.reply_text("Uso: /gastar <valor> <categoria> <descricao> <metodo>")

# Função para registrar o recebimento
async def receber(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        valor = float(context.args[0])
        descricao = " ".join(context.args[1:])  # pode adicionar uma descrição

        # Registrar o recebimento (ex: salário)
        registrar("recebimento", valor, "salario", descricao, "conta")

        # Adicionar o valor aos salários e atualizar o saldo da conta
        salarios.append(valor)
        global saldo_conta
        saldo_conta += valor

        # Resposta
        await update.message.reply_text(f"Recebimento de R${valor:.2f} registrado como '{descricao}'.")

    except:
        await update.message.reply_text("Uso: /receber <valor> <descricao>")

# Função para exibir as faturas
async def faturas_comando(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resposta = "Faturas registradas:\n"
    for fatura in faturas:
        gasto = fatura["gasto"]
        limite_restante = fatura["limite"] - gasto
        resposta += f"{fatura['nome']} - Vencimento: {fatura['vencimento']} - Gasto: R${gasto:.2f} - Limite restante: R${limite_restante:.2f}\n"
    await update.message.reply_text(resposta)

# Função para calcular o resumo
async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Mostrar o saldo da conta
    global saldo_conta
    resposta = f"Em conta - Valor: R${saldo_conta:.2f}\n"

    # Mostrar o saldo de cada cartão
    for fatura in faturas:
        limite_restante = fatura["limite"] - fatura["gasto"]
        resposta += f"Cartão de {fatura['nome']} - Valor: R${limite_restante:.2f}\n"

    await update.message.reply_text(resposta)

# Função de início
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Eu sou seu bot de controle financeiro 📊. Use /gastar, /receber ou /faturas.")

# Função principal para rodar o bot
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Registrando os comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gastar", gastar))
    app.add_handler(CommandHandler("faturas", faturas_comando))
    app.add_handler(CommandHandler("resumo", resumo))
    app.add_handler(CommandHandler("receber", receber))

    print("Bot rodando...")
    app.run_polling()

if __name__ == "__main__":
    import asyncio
    main()
