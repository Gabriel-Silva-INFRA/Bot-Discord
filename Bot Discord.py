import discord
from discord.ext import commands
from discord.ui import Select, View, Button
import mysql.connector
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

class Database:
    def __init__(self):
        self.db = mysql.connector.connect(
            host="host",
            user="user",
            password="password",
            database="database"
        )

    async def acquire(self):
        return self.db

class Empresas(Select):
    def __init__(self):
        super().__init__(
            placeholder="Escolha a Empresa",
            options=[
                discord.SelectOption(label="teste1", value="teste1"),
                discord.SelectOption(label="teste2", value="teste2"),
                discord.SelectOption(label="teste3", value="teste3"),
                discord.SelectOption(label="teste4", value="teste4"),
                discord.SelectOption(label="teste5", value="teste5"),
            ],
            custom_id="empresas"
        )
        self.selected_option = None

    async def callback(self, interaction: discord.Interaction):
        self.selected_option = interaction.data['values'][0]
        await interaction.response.send_message(f"Você selecionou a opção: {self.selected_option}")

class Area(Select):
    def __init__(self):
        super().__init__(
            placeholder="Escolha a Área Responsável: ",
            options=[
            discord.SelectOption(label="teste1", value="teste1"),
                discord.SelectOption(label="teste2", value="teste2"),
                discord.SelectOption(label="teste3", value="teste3"),
                discord.SelectOption(label="teste4", value="teste4"),
                discord.SelectOption(label="teste5", value="teste5"),
         ],
            custom_id="area"
        )
        self.selected_option = None

    async def callback(self, interaction: discord.Interaction):
        self.selected_option = interaction.data['values'][0]
        await interaction.response.send_message(f"Você selecionou a opção: {self.selected_option}")
        
        
        
class ConfirmButton(Button):
    def __init__(self, db, empresas_select, area_select):
        super().__init__(
            style=discord.ButtonStyle.green,
            label="Confirmar",
            custom_id="confirm_button"
        )
        self.db = db
        self.empresas_select = empresas_select
        self.area_select = area_select

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_name = interaction.user.name

        # Pedir ao usuário para descrever o problema
        await interaction.response.send_message("Por favor, descreva o problema.")

        # Esperar pela resposta do usuário
        try:
            description_response = await bot.wait_for(
                "message",
                check=lambda msg: msg.author.id == user_id,
                timeout=120  # 2 minutos de timeout
            )
            description = description_response.content

            # Inserir no banco de dados
            try:
                conn = await self.db.acquire()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO tickets (user_id, user_name, empresa, area, descricao) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, user_name, self.empresas_select.selected_option, self.area_select.selected_option, description))
                conn.commit()
                await interaction.followup.send(f"Ticket registrado com sucesso!")
            except Exception as e:
                print(f"Ocorreu um erro ao inserir no banco de dados: {e}")
                await interaction.followup.send("Desculpe, ocorreu um erro ao tentar registrar o ticket.")
            finally:
                cursor.close()
                conn.close()

        except asyncio.TimeoutError:
            await interaction.followup.send("Tempo esgotado. A descrição do problema não foi fornecida.")

class TicketView(discord.ui.View):
    def __init__(self, db):
        super().__init__()

        self.empresas_select = Empresas()
        self.area_select = Area()
        self.confirm_button = ConfirmButton(db, self.empresas_select, self.area_select)

        self.add_item(self.empresas_select)
        self.add_item(self.area_select)
        self.add_item(self.confirm_button)

        self.db = db

    async def on_select_option(self, interaction: discord.Interaction):
        if interaction.component.custom_id == "empresas":
            await self.empresas_select.callback(interaction)

        if interaction.component.custom_id == "area":
            await self.area_select.callback(interaction)

@bot.command()
async def ticket(ctx):
    db = Database()
    view = TicketView(db)
    
    # Envia mensagem privada para o autor do comando
    await ctx.author.send('''**Olá, bem-vindo ao nosso serviço de suporte!** 
        **Estou aqui para ajudá-lo a abrir um ticket de suporte.**
        **Por favor, forneça as seguintes informações para que eu possa ajudá-lo melhor**''', view=view)



bot.run('token')
