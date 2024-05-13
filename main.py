#!python
import json
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

with open('config.json') as config_file:
    config = json.load(config_file)

@app.route('/', methods=['GET', 'POST'])
def index():
    connection = mysql.connector.connect(
        host=config['host'],
        user=config['user'],
        password=config['password'],
        database=config['database'],
        autocommit=True
    )
    cursor = connection.cursor(prepared=True)

    if request.method == 'POST':
        gene = request.form['gene'] if request.form['gene'] else None
        primer_name = request.form['primer_name']
        sequence = request.form['sequence']
        order_date = request.form['order_date'] if request.form['order_date'] else None
        clear = request.form['clear'] if request.form['clear'] else None
        storage_location = request.form['storage_location'] if request.form['storage_location'] else None
        notes = request.form['notes'] if request.form['notes'] else None

        statement = (
            "INSERT INTO primers (gene, primer_name, sequence, order_date, clear, storage_location, notes) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        data = (gene, primer_name, sequence, order_date, clear, storage_location, notes)
        cursor.execute(statement, data)
        with open('nucleotide_primers.sql', 'r') as sql_file:
            lines = sql_file.readlines()
        unlock_index = lines.index('UNLOCK TABLES;\n')
        statement_to_file = f"INSERT INTO `primers` (`gene`, `primer_name`, `sequence`, `order_date`, `clear`, `storage_location`, `notes`) " \
                            f"VALUES ('{gene}', '{primer_name}', '{sequence}', '{order_date}', '{clear}', '{storage_location}', '{notes}');\n".replace("'None'", 'NULL')
        lines.insert(unlock_index, statement_to_file)
        with open('nucleotide_primers.sql', 'w') as sql_file:
            sql_file.writelines(lines)
        cursor.close()
        connection.close()
        return redirect(url_for('index'))

    cursor.execute('SELECT * FROM primers')
    primers = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('page.html', primers=primers)


if __name__ == '__main__':
    app.run(debug=True)
