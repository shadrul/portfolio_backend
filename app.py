from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
import os
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail, Message
from flask_cors import CORS, cross_origin
import datetime




app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
app.config['JWT_SECRET_KEY'] = 'super-secret'  # change this IRL
app.config['CORS_HEADERS'] = 'application/json'




db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
cors = CORS(app)



@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created!')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped!')


# @app.cli.command('db_seed')
# def db_seed():
#     mercury = Planet(planet_name='Mercury',
#                      planet_type='Class D',
#                      home_star='Sol',
#                      mass=2.258e23,
#                      radius=1516,
#                      distance=35.98e6)

#     venus = Planet(planet_name='Venus',
#                          planet_type='Class K',
#                          home_star='Sol',
#                          mass=4.867e24,
#                          radius=3760,
#                          distance=67.24e6)

#     earth = Planet(planet_name='Earth',
#                      planet_type='Class M',
#                      home_star='Sol',
#                      mass=5.972e24,
#                      radius=3959,
#                      distance=92.96e6)

#     db.session.add(mercury)
#     db.session.add(venus)
#     db.session.add(earth)

#     test_user = User(first_name='William',
#                      last_name='Herschel',
#                      email='test@test.com',
#                      password='P@ssw0rd')

#     db.session.add(test_user)
#     db.session.commit()
#     print('Database seeded!')



# my routes
@app.route('/')
def hello():
	return "hello"

	
@app.route('/add_user', methods=['POST'])
# @jwt_required
@cross_origin()
def add_user():
	if request.is_json:
		user_name = request.json['user_name']
		test = UserInfo.query.filter_by(user_name=user_name).first()
		if test:
			return jsonify("There is already a user by that name"), 409
		else:

			first_name = request.json['first_name']
			last_name = request.json['last_name']
			email = request.json['email']
			mobile = request.json['mobile']
			about = request.json['about']
			new_user = UserInfo(user_name=user_name,
	                            first_name=first_name,
	                            last_name=last_name,
	                            email=email,
	                            mobile=mobile,
	                            about=about)
			
			experiences = request.json['experiences']
			for i in experiences:
				organization = i['organization']
				role = i['role']
				from_date  = datetime.datetime.strptime(i['from'][:10], '%Y-%m-%d')
				to_date = datetime.datetime.strptime(i['to'][:10], '%Y-%m-%d')
				duration = (to_date.year - from_date.year) * 12 + (to_date.month - from_date.month)
				description = i['description']
				exp = Experience(organization=organization,
		                            role=role,
		                            duration=duration,
		                            description=description,
		                            user = new_user)
				
			projects = request.json['projects']
			for i in projects:
				title = i['title']
				desc = i['description']
				link = i['link']
				project = Project(title=title,
		                            desc=desc,
		                            link=link,
		                            user = new_user)
			educations = request.json['educations']
			for i in educations:
				school = i['college']
				degree = i['degree']
				description = i['description']
				from_date  = datetime.datetime.strptime(i['from'][:10], '%Y-%m-%d')
				to_date = datetime.datetime.strptime(i['to'][:10], '%Y-%m-%d')
				duration = (to_date.year - from_date.year) * 12 + (to_date.month - from_date.month)
				# duration = int(i['duration'])
				education = Education(school=school,
		                            degree=degree,
		                            description=description,
		                            duration=duration,
		                            user = new_user)
			db.session.add(new_user)
			db.session.add(exp)
			db.session.add(project)
			db.session.add(education)
			db.session.commit()
			return jsonify(message="You added a user"), 201
	else:
		# planet_name = request.form['planet_name']
		# test = Planet.query.filter_by(planet_name=planet_name).first()
		# if test:
		# 	return jsonify("There is already a planet by that name"), 409
		# else:
		# 	planet_type = request.form['planet_type']
		# 	home_star = request.form['home_star']
		# 	mass = float(request.form['mass'])
		# 	radius = float(request.form['radius'])
		# 	distance = float(request.form['distance'])
		# 	new_planet = Planet(planet_name=planet_name,
	 #                            planet_type=planet_type,
	 #                            home_star=home_star,
	 #                            mass=mass,
	 #                            radius=radius,
	 #                            distance=distance)
		# 	db.session.add(new_planet)
		# 	db.session.commit()
			return jsonify(message="in else part"), 201



@app.route('/get_user/<string:user_name>', methods=['GET'])
def get_user(user_name:str):
	test = UserInfo.query.filter_by(user_name=user_name).first()
	if(test):
		# return test.data
		user_data = user_info.dump(test)
		exp_data = exp_info.dump(test.experiences)
		project_data = project_info.dump(test.projects)
		edu_data = edu_info.dump(test.educations)
		data = jsonify({'UserData':user_data,'Experiences':exp_data, 'Projects':project_data, 'Educations':edu_data})

		return data
	else:
		return jsonify(message='User donot exist'),404


# My schemas
class UserInfo(db.Model):
    __tablename__ = 'userinfo'
    user_name = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    mobile = Column(String, unique=True)
    about = Column(Text)
    experiences = db.relationship('Experience', backref='user')
    projects = db.relationship('Project', backref='user')
    educations = db.relationship('Education', backref='user')


class Experience(db.Model):
    __tablename__ = 'experience'
    id = Column(Integer, primary_key=True)
    organization = Column(String)
    role = Column(String)
    duration = Column(Integer)
    description = Column(Text)
    user_id = Column(String, ForeignKey('userinfo.user_name'))

class Project(db.Model):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    desc = Column(String)
    link = Column(String)
    user_id = Column(String, ForeignKey('userinfo.user_name'))

class Education(db.Model):
    __tablename__ = 'education'
    id = Column(Integer, primary_key=True)
    school = Column(String)
    degree = Column(String)
    duration = Column(Integer)
    description = Column(Text)
    user_id = Column(String, ForeignKey('userinfo.user_name'))



# myschemas
class UserInfoSchema(ma.Schema):
    class Meta:
        fields = ('user_name', 'first_name', 'last_name', 'email', 'mobile', 'about')

user_info = UserInfoSchema()

class ExperienceSchema(ma.Schema):
    class Meta:
        fields = ('organization', 'role', 'duration', 'description')

exp_info = ExperienceSchema(many=True)

class ProjectSchema(ma.Schema):
    class Meta:
        fields = ('title', 'desc', 'link')

project_info = ProjectSchema(many=True)

class EducationSchema(ma.Schema):
    class Meta:
        fields = ('school', 'degree', 'duration', 'description')

edu_info = EducationSchema(many=True)

if __name__ == '__main__':
    app.run(debug=True)
