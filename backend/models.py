from extensions import bcrypt, db

# Appointments in these states free up their time slot
INACTIVE_STATUSES = ('declined', 'cancelled')


class Person(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def to_dict(self):
        return {'full_name': self.full_name, 'username': self.username, 'email': self.email, 'role': self.role}

    def __repr__(self):
        return f"<{self.__class__.__name__}('{self.full_name}', '{self.username}', '{self.email}')>"


class Client(Person):
    __tablename__ = 'client'
    role = 'client'


class Doctor(Person):
    __tablename__ = 'doctor'
    role = 'doctor'
    specialization = db.Column(db.String(80), nullable=False)

    def to_dict(self):
        return {**super().to_dict(), 'specialization': self.specialization}


ROLE_MODELS = {'client': Client, 'doctor': Doctor}


class DoctorAvailability(db.Model):
    __tablename__ = 'doctor_availability'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.String(5), nullable=False)  # "09:00"
    end_time = db.Column(db.String(5), nullable=False)    # "17:00"

    doctor = db.relationship('Doctor', backref='availabilities')

    def to_dict(self):
        return {'id': self.id, 'day_of_week': self.day_of_week, 'start_time': self.start_time, 'end_time': self.end_time}


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time_from = db.Column(db.String(10), nullable=False)
    time_to = db.Column(db.String(10), nullable=False)
    comments = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')

    doctor = db.relationship('Doctor', backref='appointments')
    client = db.relationship('Client', backref='appointments')

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date,
            'time_from': self.time_from,
            'time_to': self.time_to,
            'comments': self.comments,
            'status': self.status,
            'doctor': {'id': self.doctor.id, 'full_name': self.doctor.full_name, 'specialization': self.doctor.specialization},
            'client': {'id': self.client.id, 'full_name': self.client.full_name, 'email': self.client.email},
        }

    def __repr__(self):
        return f"<Appointment with Doctor {self.doctor.full_name} on {self.date}>"
