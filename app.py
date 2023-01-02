from flask import Flask, request, render_template, g
import sqlite3
from datetime import datetime

app = Flask(__name__)

def connect_db():
    sql = sqlite3.connect(r"C:\Users\User\Desktop\My Study Materials\web_application\food_tracker_onmyown\project_database.db")
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, "sqlite3_db"):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


@app.route("/", methods=["GET", "POST"])
def index():
    db = get_db()
    if request.method == "POST":
        req = request.form["new-day"]
        date = datetime.strptime(req, "%Y-%m-%d")

        pretty_date = datetime.strftime(date, "%B %d, %Y")
        
        data_db  = datetime.strftime(date, "%Y%m%d")
        
        # storing all the dates posted
        cur = db.execute("insert into log_date (entry_date) values (?)", [data_db])
        db.commit()

    log_date_cur= db.execute("""select id, entry_date from log_date order by entry_date desc""")
    log_date_results = log_date_cur.fetchall()
    date_results = []
    for date in log_date_results:
        single_date = {}
        single_date["entry_date"] = date["entry_date"]
        date_ = datetime.strptime(str(date["entry_date"]), "%Y%m%d")
        single_date["pretty_date"] = datetime.strftime(date_, "%B %d, %Y")
        date_results.append(single_date)

    return render_template("home.html", date_results = date_results)

@app.route("/view/<date>", methods = ["GET", "POST"])
def view(date):
    db = get_db()
    food_cur =  db.execute("""select * from food """)
    foods = food_cur.fetchall()

    dt = datetime.strptime(date, "%Y%m%d")
    pretty_date = datetime.strftime(dt, "%B %d, %Y")

    if request.method == "POST":
        id_cur = db.execute("""select id from log_date where entry_date = ?""", [date])   
        id_result= id_cur.fetchone()

        # inserting the given food into specified date
        db.execute("""insert into food_log (log_id, food_id) values (?, ?) """, [id_result['id'] , request.form["food-option"]])
        db.commit()
    
    # We are fetching all the foods given to a sepcific date.

    cur = db.execute("""select food.name, food.protein, food.carbohydrates, food.fat, food.calories 
                            from log_date 
                            join food_log on log_date.id = food_log.log_id 
                            join food on food_log.food_id = food.id
                            where log_date.entry_date = ?
                            """, [date])   
    food_results= cur.fetchall()

    total_cur = db.execute("""
    select log_date.entry_date, sum(protein) protein, sum(carbohydrates) carbohydrates, sum(fat) fat, sum(calories) calories
    from food
    join food_log on food_log.food_id = food.id
    join log_date on food_log.log_id = log_date.id
    where entry_date = ?
    group by entry_date
     """, [date])
    total_food_results = total_cur.fetchall()
        
    return render_template("day.html", foods = foods, date = date, pretty_date=pretty_date, food_results=food_results, total_food_results = total_food_results)


@app.route("/food", methods = ["GET", "POST"])
def food():

    db = get_db()

    if request.method == "POST":
        name = request.form["food-name"]
        protein = request.form["protein"]
        carbohydrates = request.form["carbohydrates"]
        fat = request.form["fat"]
        calories = (int(protein) * 4) + (int(carbohydrates) * 5) + (int(fat) * 9 )

        food_cur = db.execute("""insert into food (name, protein, carbohydrates, fat, calories)
                                values (?, ?, ?, ?, ?)""", [name, protein, carbohydrates, fat, calories])
        print(calories)                       
        db.commit()
    
    cur = db.execute("""select name, protein, carbohydrates, fat, calories 
                        from food """)
    food_results = cur.fetchall()

    return render_template("add_food.html", food_results = food_results)


if __name__ == "__main__":
    app.run(debug=True)
