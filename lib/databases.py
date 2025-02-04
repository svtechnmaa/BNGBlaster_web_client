import os
import sqlite3
import mysql.connector
from mysql.connector import Error

"""
linhnt_04/02/2025
Class for DB connection (selection between sqlite3 and mariadb).
High priority : mariadb.
If not existed: sqlite3 local.
"""
class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.db_type = os.getenv('DB_TYPE', 'sqlite').lower()  # Default to SQLite if not set

        if self.db_type == 'mariadb':
            self.host = os.getenv('DB_HOST', 'localhost')
            self.user = os.getenv('DB_USER', 'root')
            self.password = os.getenv('DB_PASSWORD', '')
            self.database = os.getenv('DB_NAME', 'default')
            self.connect_mariadb()
        elif self.db_type == 'sqlite':
            self.database = os.getenv('DB_NAME', 'blaster.db')
            self.connect_sqlite()
        else:
            raise ValueError("Unsupported DB_TYPE. Use 'mariadb' or 'sqlite'.")

    def connect_mariadb(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to MariaDB")
        except Error as e:
            print(f"Error while connecting to MariaDB: {e}")

    def connect_sqlite(self):
        try:
            self.connection = sqlite3.connect(self.database)
            print("Connected to SQLite")
        except Error as e:
            print(f"Error while connecting to SQLite: {e}")

    def close_connection(self):
        if self.connection:
            self.connection.close()
            print("Connection closed.")
    def execute_query(self, query, params=None):
        if self.connection:
            cursor = self.connection.cursor()
            try:
                cursor.execute(query, params or ())
                if query.strip().upper().startswith("SELECT"):
                    return cursor.fetchall()  # Fetch all results for SELECT queries
                else:
                    self.connection.commit()
                    return cursor.lastrowid  # Return the ID of the last inserted row for INSERT/UPDATE
            except Error as e:
                print(f"Error executing query: {e}")
            finally:
                cursor.close()
        else:
            print("No connection established.")
    def get_all_tables(self):
        if self.connection:
            cursor = self.connection.cursor()
            try:
                if self.db_type == 'mariadb':
                    cursor.execute("SHOW TABLES;")
                elif self.db_type == 'sqlite':
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                
                tables = cursor.fetchall()
                return [table[0] for table in tables]  # Extract table names from tuples
            except Error as e:
                print(f"Error fetching tables: {e}")
            finally:
                cursor.close()
        else:
            print("No connection established.")
    def delete_table(self, table_name):
        if self.connection:
            cursor = self.connection.cursor()
            try:
                query = f"DROP TABLE IF EXISTS {table_name};"
                cursor.execute(query)
                self.connection.commit()
                print(f"Table '{table_name}' deleted successfully.")
            except Error as e:
                print(f"Error deleting table '{table_name}': {e}")
            finally:
                cursor.close()
        else:
            print("No connection established.")
    def insert(self, table_name, data):
        """
        Insert a new record into the specified table.

        :param table_name: Name of the table to insert into.
        :param data: A dictionary where keys are column names and values are the values to insert.
        :return: The ID of the last inserted row.
        """
        if self.connection:
            cursor = self.connection.cursor()
            try:
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['%s'] * len(data)) if self.db_type == 'mariadb' else ', '.join(['?'] * len(data))
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"
                cursor.execute(query, list(data.values()))
                self.connection.commit()
                print(f"Inserted record into '{table_name}': {data}")
                return cursor.lastrowid  # Return the ID of the last inserted row
            except Error as e:
                print(f"Error inserting into table '{table_name}': {e}")
            finally:
                cursor.close()
        else:
            print("No connection established.")
    def update(self, table_name, data, condition):
        """
        Update records in the specified table.

        :param table_name: Name of the table to update.
        :param data: A dictionary where keys are column names and values are the new values to set.
        :param condition: A string representing the condition for the update (e.g., "id = 1").
        """
        if self.connection:
            cursor = self.connection.cursor()
            try:
                # Create the SET clause
                if self.db_type == 'sqlite':
                    set_clause = ', '.join([f"{key} = ?" for key in data.keys()])  # Use ? for SQLite
                else:
                    set_clause = ', '.join([f"{key} = %s" for key in data.keys()])  # Use %s for MariaDB

                query = f"UPDATE {table_name} SET {set_clause} WHERE {condition};"
                cursor.execute(query, list(data.values()))
                self.connection.commit()
                print(f"Updated records in '{table_name}' where {condition}.")
            except Error as e:
                print(f"Error updating records in table '{table_name}': {e}")
            finally:
                cursor.close()
        else:
            print("No connection established.")
    def delete(self, table_name, condition):
        """
        Delete a record from the specified table.

        :param table_name: Name of the table to delete from.
        :param condition: A string representing the condition for the delete (e.g., "id = 1").
        """
        if self.connection:
            cursor = self.connection.cursor()
            try:
                query = f"DELETE FROM {table_name} WHERE {condition};"
                cursor.execute(query)
                self.connection.commit()
                print(f"Deleted record from '{table_name}' where {condition}.")
            except Error as e:
                print(f"Error deleting record from table '{table_name}': {e}")
            finally:
                cursor.close()
        else:
            print("No connection established.")
# Example usage
if __name__ == "__main__":
    db = DatabaseConnection()
    # Example query
    # result = db.execute_query("SELECT * FROM your_table")
    # print(result)
    db.close_connection()