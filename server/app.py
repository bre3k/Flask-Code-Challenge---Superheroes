from flask import Flask, request
from flask_restful import Api, Resource
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower

app = Flask(__name__)

# Configurations for the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///superheroes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

# Heroes Resource
class Heroes(Resource):
    def get(self):
        heroes = Hero.query.all()
        return [hero.to_dict(only=('id', 'name', 'super_name')) for hero in heroes], 200

# Hero by ID Resource
class HeroById(Resource):
    def get(self, id):
        hero = db.session.get(Hero, id)
        if hero:
            return hero.to_dict(only=('id', 'name', 'super_name', 'hero_powers')), 200
        else:
            return {'error': 'Hero not found'}, 404

# Powers Resource
class Powers(Resource):
    def get(self):
        powers = Power.query.all()
        return [power.to_dict(only=('id', 'name', 'description')) for power in powers], 200

# Power by ID Resource
class PowerById(Resource):
    def get(self, id):
        power = db.session.get(Power, id)
        if power:
            return power.to_dict(only=('id', 'name', 'description')), 200
        else:
            return {'error': 'Power not found'}, 404

    def patch(self, id):
        power = db.session.get(Power, id)
        if power:
            data = request.get_json()
            try:
                if 'description' in data:
                    if len(data['description']) < 20:
                        raise ValueError('Description must be at least 20 characters long.')
                    power.description = data['description']
                db.session.commit()
                return power.to_dict(only=('id', 'name', 'description')), 200
            except ValueError as e:
                return {'errors': [str(e)]}, 400
        else:
            return {'error': 'Power not found'}, 404

# HeroPowers Resource
class HeroPowers(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_hero_power = HeroPower(
                strength=data['strength'],
                hero_id=data['hero_id'],
                power_id=data['power_id']
            )
            db.session.add(new_hero_power)
            db.session.commit()
            return new_hero_power.to_dict(), 201  # Ensure status 201 Created
        except ValueError as e:
            return {'errors': [str(e)]}, 400

# Registering routes
api.add_resource(Heroes, '/heroes')
api.add_resource(HeroById, '/heroes/<int:id>')
api.add_resource(Powers, '/powers')
api.add_resource(PowerById, '/powers/<int:id>')
api.add_resource(HeroPowers, '/hero_powers')

# Running the app
if __name__ == '__main__':
    app.run(debug=True)
