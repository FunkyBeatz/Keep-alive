import discord
from discord.ext import commands
from discord import app_commands  
import os
from flask import Flask
from threading import Thread
from keep_alive import keep_alive


# Create a bot object with the necessary intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)





# Sync slash commands when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    if not hasattr(bot, 'synced'):
        try:
            synced = await bot.tree.sync()  # Syncs the slash commands
            bot.synced = True  # Prevents multiple syncs
            print(f'Synced {len(synced)} command(s)')
        except Exception as e:
            print(f"Error syncing commands: {e}")

@bot.command(name="sync_commands")      # Forces the bot to sync (Use in Dc channel)
@commands.has_permissions(administrator=True)  # Optional: Only allow admins to sync
async def sync_commands(ctx):
    try:
        synced = await bot.tree.sync()
        await ctx.send(f'Synced {len(synced)} command(s).')
    except Exception as e:
        await ctx.send(f"Error syncing commands: {e}")


# Define a slash command to store Solana wallet addresses
@bot.tree.command(name="store_wallet", description="Store a Solana wallet address.")
async def store_wallet(interaction: discord.Interaction, wallet_address: str):
    # Defer the interaction to avoid timeout
    await interaction.response.defer(ephemeral=True)

    # Validate Solana wallet address (optional)
    if len(wallet_address) != 44:
        await interaction.followup.send("Invalid Solana wallet address. Please check and try again.", ephemeral=True)
        return

    # Store the wallet address in a file
    with open("solana_wallets.txt", "a") as wallet_file:
        wallet_file.write(f'{interaction.user.name}#{interaction.user.discriminator}: {wallet_address}\n')

    # Follow-up message after processing
    await interaction.followup.send(f'Wallet address saved for {interaction.user.name}.', ephemeral=True)

# Prefix command to send the file with stored wallet addresses
@bot.command(name="get_wallets")
async def get_wallets(ctx):
    file_path = "solana_wallets.txt"

    # Check if the file exists
    if os.path.exists(file_path):
        await ctx.send("Here are the stored wallet addresses:", file=discord.File(file_path))
    else:
        await ctx.send("No wallet addresses have been stored yet.")


# Prefix command to clear the wallet list (delete or empty the file)
@bot.command(name="clear_wallets")
async def clear_wallets(ctx):
    file_path = "solana_wallets.txt"

    # Check if the file exists
    if os.path.exists(file_path):
        # Empty the contents of the file
        with open(file_path, "w") as wallet_file:
            wallet_file.write("")  # Writing an empty string clears the file

        await ctx.send("The wallet list has been cleared.")
    else:
        await ctx.send("No wallet list found to clear.")

# Define a slash command to edit Solana wallet addresses
@bot.tree.command(name="edit_wallets", description="Edit your current Solana wallet address to a new one.")
async def edit_wallets(interaction: discord.Interaction, current_wallet: str, new_wallet: str):
    await interaction.response.defer(ephemeral=True)  # Defer the response to prevent timeout

    # Validate the current wallet address (must be exactly 44 characters for Solana)
    if len(current_wallet) != 44:
        await interaction.followup.send(
            "Invalid current Solana wallet address. Please ensure the address is exactly 44 characters.", ephemeral=True)
        return

    # Validate the new wallet address (must be exactly 44 characters for Solana)
    if len(new_wallet) != 44:
        await interaction.followup.send(
            "Invalid new Solana wallet address. Please ensure the address is exactly 44 characters.", ephemeral=True)
        return

    # Logic to edit the wallet
    file_path = "solana_wallets.txt"
    if not os.path.exists(file_path):
        await interaction.followup.send("No wallet addresses have been stored yet.", ephemeral=True)
        return

    # Read file and update the wallet
    with open(file_path, "r") as wallet_file:
        lines = wallet_file.readlines()

    user_id = f'{interaction.user.name}#{interaction.user.discriminator}'
    found = False

    # Write the updated file back
    with open(file_path, "w") as wallet_file:
        for line in lines:
            if line.startswith(user_id) and current_wallet in line:
                # Replace the old wallet with the new one
                wallet_file.write(f'{user_id}: {new_wallet}\n')
                found = True
            else:
                wallet_file.write(line)

    if found:
        await interaction.followup.send(
            f"Your wallet address has been updated from {current_wallet} to {new_wallet}.", ephemeral=True)
    else:
        await interaction.followup.send(
            f"Could not find the wallet address {current_wallet}. Please make sure it is correct.", ephemeral=True)




# This will start the Flask server
keep_alive()
token = os.getenv("DISCORD_BOT_TOKEN") # Made the token a secret, so no one can see it
# Even in github, so I can push it from git Bash

if token is None:
    print("DISCORD_BOT_TOKEN environment variable not found. Please set it.")
    exit(1)
bot.run(token) # Start the bot with your token
