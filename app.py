from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///college.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'localhost')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 25))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', False)
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@kmggp.edu')

db = SQLAlchemy(app)
mail = Mail(app)

# Database Models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    course = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')

    def __repr__(self):
        return f'<Student {self.name}>'

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='new')

    def __repr__(self):
        return f'<Contact {self.name}>'

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    image_url = db.Column(db.String(255))

    def __repr__(self):
        return f'<News {self.title}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Event {self.title}>'

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Admin {self.username}>'

# Routes
@app.route('/')
def index():
    news = News.query.order_by(News.created_at.desc()).limit(3).all()
    events = Event.query.filter(Event.event_date >= datetime.utcnow()).order_by(Event.event_date).limit(5).all()
    return render_template('index.html', news=news, events=events)

@app.route('/admission', methods=['GET', 'POST'])
def admission():
    if request.method == 'POST':
        try:
            student = Student(
                name=request.form.get('name'),
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                address=request.form.get('address'),
                course=request.form.get('course'),
                qualification=request.form.get('qualification')
            )
            db.session.add(student)
            db.session.commit()
            
            # Send confirmation email
            send_admission_email(student)
            
            flash('Admission form submitted successfully! Check your email for confirmation.', 'success')
            return redirect(url_for('admission'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('admission.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            contact = Contact(
                name=request.form.get('name'),
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                subject=request.form.get('subject'),
                message=request.form.get('message')
            )
            db.session.add(contact)
            db.session.commit()
            
            # Send email notification
            send_contact_email(contact)
            
            flash('Thank you for contacting us! We will respond soon.', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('contact.html')

@app.route('/news')
def news():
    page = request.args.get('page', 1, type=int)
    news = News.query.order_by(News.created_at.desc()).paginate(page=page, per_page=6)
    return render_template('news.html', news=news)

@app.route('/events')
def events():
    events = Event.query.order_by(Event.event_date).all()
    return render_template('events.html', events=events)

@app.route('/admin')
def admin_dashboard():
    student_count = Student.query.count()
    contact_count = Contact.query.count()
    news_count = News.query.count()
    event_count = Event.query.count()
    
    recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
    recent_contacts = Contact.query.order_by(Contact.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         student_count=student_count,
                         contact_count=contact_count,
                         news_count=news_count,
                         event_count=event_count,
                         recent_students=recent_students,
                         recent_contacts=recent_contacts)

@app.route('/admin/students')
def admin_students():
    students = Student.query.all()
    return render_template('admin/students.html', students=students)

@app.route('/admin/contacts')
def admin_contacts():
    contacts = Contact.query.all()
    return render_template('admin/contacts.html', contacts=contacts)

@app.route('/admin/news', methods=['GET', 'POST'])
def admin_news():
    if request.method == 'POST':
        try:
            news = News(
                title=request.form.get('title'),
                content=request.form.get('content'),
                image_url=request.form.get('image_url')
            )
            db.session.add(news)
            db.session.commit()
            flash('News added successfully!', 'success')
            return redirect(url_for('admin_news'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    
    news = News.query.all()
    return render_template('admin/news.html', news=news)

@app.route('/admin/events', methods=['GET', 'POST'])
def admin_events():
    if request.method == 'POST':
        try:
            event = Event(
                title=request.form.get('title'),
                description=request.form.get('description'),
                event_date=datetime.fromisoformat(request.form.get('event_date')),
                location=request.form.get('location'),
                image_url=request.form.get('image_url')
            )
            db.session.add(event)
            db.session.commit()
            flash('Event added successfully!', 'success')
            return redirect(url_for('admin_events'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    
    events = Event.query.all()
    return render_template('admin/events.html', events=events)

@app.route('/admin/delete-student/<int:id>')
def delete_student(id):
    student = Student.query.get(id)
    if student:
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted!', 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/delete-contact/<int:id>')
def delete_contact(id):
    contact = Contact.query.get(id)
    if contact:
        db.session.delete(contact)
        db.session.commit()
        flash('Contact deleted!', 'success')
    return redirect(url_for('admin_contacts'))

def send_admission_email(student):
    try:
        msg = Message(
            subject='Admission Form Confirmation - KM Mayawati Government Girls Polytechnic',
            recipients=[student.email],
            html=f'''
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2 style="color: #1a472a;">Thank you for applying!</h2>
                    <p>Dear {student.name},</p>
                    <p>Your admission form for <strong>{student.course}</strong> has been successfully submitted.</p>
                    <p><strong>Details:</strong></p>
                    <ul>
                        <li>Name: {student.name}</li>
                        <li>Email: {student.email}</li>
                        <li>Course: {student.course}</li>
                    </ul>
                    <p>We will review your application and contact you soon.</p>
                    <p>Best regards,<br><strong>KM Mayawati Government Girls Polytechnic</strong></p>
                </body>
            </html>
            '''
        )
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {str(e)}")

def send_contact_email(contact):
    try:
        msg = Message(
            subject=f'New Contact Message: {contact.subject}',
            recipients=['principal@kmggp.edu'],
            html=f'''
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2 style="color: #1a472a;">New Contact Message</h2>
                    <p><strong>From:</strong> {contact.name}</p>
                    <p><strong>Email:</strong> {contact.email}</p>
                    <p><strong>Phone:</strong> {contact.phone}</p>
                    <p><strong>Subject:</strong> {contact.subject}</p>
                    <p><strong>Message:</strong></p>
                    <p>{contact.message}</p>
                </body>
            </html>
            '''
        )
        mail.send(msg)
        
        # Send confirmation email to user
        user_msg = Message(
            subject='We received your message',
            recipients=[contact.email],
            html=f'''
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2 style="color: #1a472a;">Thank you for contacting us!</h2>
                    <p>Dear {contact.name},</p>
                    <p>We have received your message and will respond as soon as possible.</p>
                    <p>Best regards,<br><strong>KM Mayawati Government Girls Polytechnic</strong></p>
                </body>
            </html>
            '''
        )
        mail.send(user_msg)
    except Exception as e:
        print(f"Error sending email: {str(e)}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
