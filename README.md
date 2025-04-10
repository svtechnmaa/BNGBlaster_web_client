# BNGBlaster_web_client
A quick draft of a web-based user interface for bngblaster network tester, based mostly on streamlit and jinja2

Options for use DB: High priority : mariadb. If not existed: use sqlite3 local.
  1. Sqlite3 local
  2. MariaDB: export enviroment variable for configuring DB on MariaDB external
  ```
  DB_HOST=""
  DB_USER=""
  DB_PASSWORD=""
  DB_NAME=""
  ```
