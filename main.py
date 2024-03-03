import discord
import random
from discord.ui import Select, View
from discord.ext import commands
from typing import List, Literal, TypedDict
from typing_extensions import NotRequired, Required


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=commands.when_mentioned_or("$"), intents=intents
        )

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")


bot = Bot()


def select_account(accounts_file):
    with open(accounts_file, "r") as f:
        accounts = f.readlines()
    accounts = [account.strip() for account in accounts]
    available_accounts = [
        account for account in accounts if account not in sent_accounts
    ]
    if available_accounts:
        selected_account = random.choice(available_accounts)
        return selected_account
    else:
        return None


class Dropdown(discord.ui.Select):
    def __init__(self):

        self.cooldown = commands.CooldownMapping.from_cooldown(
            1, 300, commands.BucketType.member
        )

        options = [
            discord.SelectOption(label="HBO", description=""),
            discord.SelectOption(label="crunchyroll", description=""),
            discord.SelectOption(label="Disney +", description=""),
            discord.SelectOption(label="Steam", description=""),
        ]

        super().__init__(
            placeholder="Elige tu generador",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        interaction.message.author = interaction.user
        bucket = self.cooldown.get_bucket(interaction.message)
        retry = bucket.update_rate_limit()

        global sent_accounts
        service = self.values[0].lower()

        account_files = {
            "hbo": "hbo_accounts.txt",
            "crunchyroll": "crunchyroll_accounts.txt",
            "disney +": "disneyplus_accounts.txt",
            "steam": "steam_accounts.txt",
        }

        if retry:
            return await interaction.response.send_message(
                f"Slow down Nigga! Try again in {round(retry, 1)} seconds.",
                ephemeral=True,
            )
        accounts_file = account_files.get(service)
        if accounts_file:
            selected_account = select_account(accounts_file)
            if selected_account:
                await interaction.response.send_message(
                    f"Seleccionaste {self.values[0]}",
                    ephemeral=True,
                )
                await interaction.user.send(
                    f"Seleccionaste {self.values[0]}, {selected_account}",
                    ephemeral=True,
                )
                with open("cuentas_enviadas.txt", "a") as f:
                    f.write(selected_account + "\n")
                with open(accounts_file, "r") as f:
                    lines = f.readlines()
                with open(accounts_file, "w") as f:
                    for line in lines:
                        if line.strip() != selected_account:
                            f.write(line)
            else:
                await interaction.response.send_message(
                    "No hay cuentas disponibles para este servicio.",
                    ephemeral=True,
                )
        else:
            await interaction.response.send_message(
                "Servicio no válido.",
                ephemeral=True,
            )


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Dropdown())


class EmbedFooter(TypedDict):
    text: str
    icon_url: NotRequired[str]
    proxy_icon_url: NotRequired[str]


class EmbedImage(TypedDict, total=False):
    url: Required[str]
    proxy_url: str
    height: int
    width: int


class Embed(TypedDict, total=False):
    title: str
    description: str
    color: int
    image: EmbedImage
    footer: EmbedFooter


class Embedview(discord.Embed):
    def __init__(self, data: Embed):
        super().__init__(
            title=data.get("title", ""),
            description=data.get("description", ""),
            color=data.get("color", 0),
        )
        image_data = data.get("image", {})
        self.set_image(url=image_data["url"])
        self.set_footer(
            text=data.get("footer", {}).get("text", ""),
            icon_url=data.get("footer", {}).get("icon_url", ""),
        )


@bot.event
async def on_command_error(ctx: discord.ext.commands.context.Context, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"This command is on a {error.retry_after:.2f}s cooldown", ephemeral=True
        )


@bot.command()
# @commands.cooldown(1, 300, commands.BucketType.user)
async def hello(ctx):

    embed = {
        "title": "🇪🇦 － Hola @Gen Premium,bienvenido al panel del Generador Premium.",
        "description": "¡Para Generar una cuenta debes seleccionar un servicio del menú!",
        "color": discord.Color.red().value,
        "image": {
            "url": "https://academy.avast.com/hs-fs/hubfs/New_Avast_Academy/Hackers/Hacker-Hero-a1.png?width=1200&name=Hacker-Hero-a1.png"
        },
        "footer": {"text": "by Dev_7274"},
    }

    view = DropdownView()

    descripcion = Embedview(embed)

    await ctx.send(embed=descripcion, view=view)


from config import TOKEN

sent_accounts = []

bot.run(TOKEN)
