import discord
from discord.ext import commands
import sqlite3
import textwrap

# SQLite Database Connection
conn = sqlite3.connect('items.db')
c = conn.cursor()


# Fetch and display table data
async def display_table(channel):
    await channel.purge()  # Clear existing messages in the channel.
    await channel.send('/addItem quantity "name" category || *quotes around name is very important*')
    await channel.send("/removeItem item_id")
    await channel.send("/updateQuantity item_id number || *can use +number, -number, or set number to desired value (ex: +5, -7 or 250)*")
    await channel.send('/updateName item_id "name"')
    await channel.send("/updateCategory item_id category")
    await channel.send('usage ex: **/updateQuantity 2 +5000** || *this would add 5000 gold (item_id 2) to party funds*')
    c.execute('SELECT * FROM items ORDER BY category')  # Query the database.
    data = c.fetchall()

    # Formatting and Discord's character limit
    max_name_length = 65  
    char_limit = 2000
    header_format = "| {:<6} | {:<" + str(max_name_length) + "} | {:<8} |"
    row_format = "| {:<6} | {:<" + str(max_name_length) + "} | {:<8} |"

    table = ""
    last_category = None
    subtable_length = 0

    for row in data:
        if last_category != row[3]:
            # Send existing table(s), if any
            if table:
                await channel.send(f"```{table}```")

            # Reset for new category
            table = ""
            subtable_length = 0

            table += f"\n\n**{row[3]}**\n"
            header = header_format.format("ID", "Name", "Quantity") 
            delimiter = "-" * 89  # Total row length
            table += delimiter + "\n" + header + "\n" + delimiter
            subtable_length += len(delimiter) + len(header) + len(delimiter)
            last_category = row[3]

        wrapped_name = textwrap.fill(row[2], max_name_length, break_long_words=False, replace_whitespace=False)
        
        for i, line in enumerate(wrapped_name.split('\n')):
            row_string = row_format.format(row[0] if i == 0 else '', line, row[1] if i == 0 else '')
            
            if subtable_length + len(row_string) >= char_limit:
                # Send current subtable and reset
                await channel.send(f"```{table}```")
                table = ""
                subtable_length = 0
                table += delimiter + "\n" + header + "\n" + delimiter  # Subtable header
                subtable_length += len(delimiter) + len(header) + len(delimiter)

            table += "\n" + row_string
            subtable_length += len(row_string)

    
    # Send last table or subtable
    if table:
        await channel.send(f"```{table}```")
    else:
        await channel.send("No items to display.")


# Add data to table
@commands.command()
async def addItem(ctx, quantity: int, name: str, category: str):
    name_title_case = name.title()
    category_title_case = category.title()

    # Check if item exists without considering case
    c.execute("SELECT id, name, quantity, category FROM items WHERE name COLLATE NOCASE = ?", (name_title_case,))
    if c.fetchone():
        await ctx.send("Item already exists.")
        return

    c.execute("INSERT INTO items (quantity, name, category) VALUES (?, ?, ?)",
              (quantity, name_title_case, category_title_case))
    conn.commit()
    c.execute("SELECT id FROM items WHERE name = ?", (name_title_case,))
    result = c.fetchone()

    await ctx.send(f"item {name_title_case} succesfully added to {category_title_case} (item id {result[0]})")
    # await display_table(ctx.channel)

# Remove data from table
@commands.command()
async def removeItem(ctx, item_id: int):
    c.execute("SELECT name FROM items WHERE id = ?", (item_id,))
    result = c.fetchone()

    c.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    
    await ctx.send(f"item {result[0]} succesfully removed")
    # await display_table(ctx.channel)

# Update data in the table
@commands.command()
async def updateQuantity(ctx, item_id: int, quantity_str: str):
    # Check if the quantity string starts with '+' or '-'
    if quantity_str.startswith('+') or quantity_str.startswith('-'):
        # Fetch current quantity from database
        c.execute("SELECT name, quantity FROM items WHERE id = ?", (item_id,))
        result = c.fetchone()
        
        
        # If the item doesn't exist, return a message and exit
        if result[1] is None:
            await ctx.send("Item ID does not exist.")
            return
        
        current_quantity = result[1]
        
        # Parse the quantity to be added or subtracted
        delta_quantity = int(quantity_str)
        
        # Compute the new quantity
        new_quantity = current_quantity + delta_quantity

        if new_quantity < current_quantity:
            c.execute("UPDATE items SET quantity = ? WHERE id = ?", (new_quantity, item_id))
            conn.commit()
            await ctx.send(f"succesfully subtracted {delta_quantity * -1} {result[0]}")
        elif new_quantity > current_quantity:
            c.execute("UPDATE items SET quantity = ? WHERE id = ?", (new_quantity, item_id))
            conn.commit()
            await ctx.send(f"succesfully added {delta_quantity} {result[0]} ")   

    else:
        # Directly set the new quantity
        new_quantity = int(quantity_str)
        c.execute("UPDATE items SET quantity = ? WHERE id = ?", (new_quantity, item_id))
        conn.commit()
        await ctx.send(f"item {result[0]} succesfully updated from {quantity_str} to {new_quantity}")
    
    # Update the database
    # await display_table(ctx.channel)


# Update the name of an item
@commands.command()
async def updateName(ctx, item_id: int, name: str):
    name_title_case = name.title()  # Convert the name to title case
    c.execute("SELECT name FROM items WHERE id = ?", (item_id,))
    result = c.fetchone()
    c.execute("UPDATE items SET name = ? WHERE id = ?", (name_title_case, item_id))
    conn.commit()
    await ctx.send(f"item {result[0]} succesfully updated to {name_title_case}")
    # await display_table(ctx.channel)

# Update the category of an item
@commands.command()
async def updateCategory(ctx, item_id: int, category: str):
    category_title_case = category.title()  # Convert the category to title case
    c.execute("SELECT name, category FROM items WHERE id = ?", (item_id,))
    result = c.fetchone()
    c.execute("UPDATE items SET category = ? WHERE id = ?", (category_title_case, item_id))
    conn.commit()
    await ctx.send(f"category of item {result[0]} succesfully updated to {category_title_case} from {result[1]}")
    # await display_table(ctx.channel)