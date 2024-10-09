import re
import asyncio
import argparse  # For command-line argument parsing
from ElementalDB import ElementalDB

class EDLangCompiler:
    def __init__(self):
        self.db = ElementalDB()

    async def compile(self, script_path):
        with open(script_path, "r") as file:
            commands = file.readlines()
            for command in commands:
                await self.parse_command(command.strip())

    async def parse_command(self, command):
        create_pattern = r"create table (\w+) schema \[(.+)\]"
        add_pattern = r"add (\w+) \[(.+)\]"
        update_pattern = r"update (\w+) \[(.+)\] \[(.+)\]"
        delete_pattern = r"delete (\w+) \[(.+)\]"
        select_pattern = r"select (\w+) \[(.+)\]"

        if match := re.match(create_pattern, command):
            await self.handle_create(match, create_pattern)
        elif match := re.match(add_pattern, command):
            await self.handle_add(match, add_pattern)
        elif match := re.match(update_pattern, command):
            await self.handle_update(match, update_pattern)
        elif match := re.match(delete_pattern, command):
            await self.handle_delete(match, delete_pattern)
        elif match := re.match(select_pattern, command):
            await self.handle_select(match, select_pattern)

    async def handle_create(self, match, create_pattern):
        table_name = match.group(1)
        schema = match.group(2).split(", ")
        schema = [(col, "TEXT") for col in schema]
        self.db.create_table(table_name, schema)
        print(f"Table '{table_name}' created with schema {schema}")

    async def handle_add(self, match, add_pattern):
        table_name = match.group(1)
        values = eval(match.group(2))
        await self.db.add(table_name, values)
        print(f"Record {values} added to table '{table_name}'")

    async def handle_update(self, match, update_pattern):
        table_name = match.group(1)
        old_values = eval(match.group(2))
        new_values = eval(match.group(3))
        record = await self.db.get(table_name, 'id', old_values[0])  # Assume 'id' is the first element
        if record:
            await self.db.update(table_name, record['id'], dict(zip(record.keys(), new_values)))
            print(f"Record updated from {old_values} to {new_values}")
        else:
            print(f"Record {old_values} not found in table '{table_name}'")

    async def handle_delete(self, match, delete_pattern):
        table_name = match.group(1)
        values = eval(match.group(2))
        await self.db.delete(table_name, values)

    async def handle_select(self, match, select_pattern):
        table_name = match.group(1)
        values = eval(match.group(2))
        record = await self.db.get(table_name, 'id', values[0])  # Assuming the first value is 'id'
        if record:
            print(f"Record found: {record}")
        else:
            print(f"Record {values} not found in table '{table_name}'")


# Command-line argument parsing and script execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run EDLang script")
    parser.add_argument('-r', '--run', type=str, required=True, help="File name of the EDLang script to run")

    args = parser.parse_args()

    # Run the compiler with asyncio and the provided file name
    compiler = EDLangCompiler()
    asyncio.run(compiler.compile(args.run))
