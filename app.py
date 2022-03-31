import requests
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
load_dotenv()
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SECRET_KEY'] = "os.getenv(SECRET_KEY)"

db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable = False)

def get_weather_data(city):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid=1f7cf6754b5a9f95360e4832fa3c78f6'
    r = requests.get(url).json()
    return r

@app.route("/")
def get_index():
    weather_data = []
    cities = City.query.all() 
 
    for city in cities:    
        r = get_weather_data(city.name)
        
        temperate = float(r['main']['temp'])
        temp = temperate - 273.15
        #print(r)

        weather = {
            'city': city.name,
            'temperature': temp,
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon']
        }
        weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data)    

           
@app.route("/", methods=['POST'])
def post_index():
    err_msg = ''
    new_city =request.form.get('city')
    print(new_city)
    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()
        if not existing_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                err_msg ="City does not exist"
           #     flash(f'{err_msg}', "alert-danger")

        else:
           err_msg = "City already exist in the database" 
       #    flash(f'{err_msg}', "alert-danger")
    if err_msg:
        flash(f'{err_msg}', "alert-danger")
    else:
        flash('Success', "alert-success")    

    return redirect(url_for('get_index'))           


@app.route("/delete/<name>")
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()

    return redirect(url_for('get_index'))





if __name__ == "__main__":
    app.run(debug=True)    