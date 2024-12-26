from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from datetime import datetime
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import click

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

    
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # تأكد من وجود هذا السطر
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    name_ar = db.Column(db.String(50), nullable=False)
    projects = db.relationship('Project', backref='category_rel', lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    main_image = db.Column(db.String(200))
    images = db.relationship('ProjectImage', backref='project', lazy=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    location = db.Column(db.String(100))
    area = db.Column(db.String(50))
    completion_year = db.Column(db.String(4))
    featured = db.Column(db.Boolean, default=False)

class ProjectImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    settings = SiteSettings.query.first()
    if request.method == 'POST':
        try:
            new_request = ContactRequest(
                name=request.form['name'],
                email=request.form['email'],
                phone=request.form['phone'],
                message=request.form['message']
            )
            db.session.add(new_request)
            db.session.commit()
            flash('تم إرسال رسالتك بنجاح! سنتواصل معك قريباً.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('حدث خطأ أثناء إرسال الرسالة. الرجاء المحاولة مرة أخرى.', 'danger')
            app.logger.error(f'Error in contact form: {str(e)}')
            return redirect(url_for('contact'))
    return render_template('contact.html', settings=settings)
class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    intro_text = db.Column(db.Text)
    phone_number = db.Column(db.String(20))
    whatsapp_number = db.Column(db.String(20))
    facebook_url = db.Column(db.String(200))
    twitter_url = db.Column(db.String(200))
    instagram_url = db.Column(db.String(200))
    linkedin_url = db.Column(db.String(200))
    # Hero Section
    hero_title = db.Column(db.String(200), default="نوايف الخليج للاستشارات الهندسية")
    hero_subtitle = db.Column(db.String(500), default="نقدم حلولاً هندسية مبتكرة تجمع بين الإبداع والاستدامة")
    hero_image = db.Column(db.String(200))
    # Services Section
    service1_title = db.Column(db.String(200), default="التصميم المعماري")
    service1_description = db.Column(db.Text, default="نقدم حلول تصميم معمارية مبتكرة تجمع بين الجمال والوظيفة")
    service1_icon = db.Column(db.String(50), default="fas fa-building")
    service2_title = db.Column(db.String(200), default="التصميم الداخلي")
    service2_description = db.Column(db.Text, default="نصمم مساحات داخلية تعكس هوية المكان وتلبي احتياجات المستخدمين")
    service2_icon = db.Column(db.String(50), default="fas fa-pencil-ruler")
    service3_title = db.Column(db.String(200), default="التخطيط العمراني")
    service3_description = db.Column(db.Text, default="نخطط المدن والمجتمعات العمرانية بأسلوب مستدام وعصري")
    service3_icon = db.Column(db.String(50), default="fas fa-city")
    # Stats Section
    stats_image = db.Column(db.String(200))
    stats_projects = db.Column(db.Integer, default=150)
    stats_experience = db.Column(db.Integer, default=10)
    stats_clients = db.Column(db.Integer, default=50)
    stats_employees = db.Column(db.Integer, default=20)
    # Testimonials
    show_testimonials = db.Column(db.Boolean, default=True)
    testimonial1_name = db.Column(db.String(100), default="أحمد محمد")
    testimonial1_position = db.Column(db.String(100), default="مدير شركة عقارية")
    testimonial1_text = db.Column(db.Text, default="تجربة رائعة مع فريق نوايف الخليج. احترافية عالية وتصاميم مبتكرة")
    testimonial1_image = db.Column(db.String(200))
    testimonial2_name = db.Column(db.String(100), default="خالد العتيبي")
    testimonial2_position = db.Column(db.String(100), default="مستثمر عقاري")
    testimonial2_text = db.Column(db.Text, default="فريق متميز يقدم حلول إبداعية تتجاوز التوقعات")
    testimonial2_image = db.Column(db.String(200))
    testimonial3_name = db.Column(db.String(100), default="سعد الشمري")
    testimonial3_position = db.Column(db.String(100), default="مطور عقاري")
    testimonial3_text = db.Column(db.Text, default="الدقة في التنفيذ والالتزام بالمواعيد من أهم ما يميز نوايف الخليج")
    testimonial3_image = db.Column(db.String(200))
    # CTA Section
    cta_title = db.Column(db.String(200), default="هل لديك مشروع تريد تنفيذه؟")
    cta_subtitle = db.Column(db.String(500), default="نحن هنا لمساعدتك في تحقيق رؤيتك المعمارية")
    
class ContactRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='new')  # new, read, responded
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PageContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(50), nullable=False)
    section = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(20), default='text')  # text, image, html
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('page', 'section', name='unique_page_section'),
    )

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def utility_processor():
    settings = SiteSettings.query.first()
    return {
        'now': datetime.now(),
        'settings': settings
    }

@app.route('/')
def home():
    settings = SiteSettings.query.first()
    featured_projects = Project.query.filter_by(featured=True).limit(6).all()
    return render_template('home.html', settings=settings, featured_projects=featured_projects)

@app.route('/projects')
def projects():
    category = request.args.get('category', 'all')
    if category != 'all':
        projects = Project.query.filter_by(category_id=category).all()
    else:
        projects = Project.query.all()
    settings = SiteSettings.query.first()
    return render_template('projects.html', projects=projects, settings=settings, active_category=category)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    settings = SiteSettings.query.first()
    return render_template('project_detail.html', project=project, settings=settings)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
    
    # Get statistics
    new_requests_count = ContactRequest.query.filter_by(status='new').count()
    projects_count = Project.query.count()
    categories_count = Category.query.count()
    
    # Get recent activities
    recent_activities = []
    
    # Add recent contact requests to activities
    for req in ContactRequest.query.order_by(ContactRequest.created_at.desc()).limit(3):
        recent_activities.append({
            'title': 'طلب اتصال جديد',
            'description': f'تم استلام طلب اتصال من {req.name}',
            'timestamp': req.created_at
        })
    
    # Add recent content updates to activities
    for content in PageContent.query.order_by(PageContent.last_updated.desc()).limit(3):
        recent_activities.append({
            'title': 'تحديث محتوى',
            'description': f'تم تحديث محتوى صفحة {content.page} - قسم {content.section}',
            'timestamp': content.last_updated
        })
    
    # Sort activities by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = recent_activities[:5]
    
    return render_template('admin.html',
                         new_requests_count=new_requests_count,
                         projects_count=projects_count,
                         categories_count=categories_count,
                         recent_activities=recent_activities)

@app.route('/admin/project/add', methods=['GET', 'POST'])
@login_required
def add_project():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        location = request.form.get('location')
        area = request.form.get('area')
        completion_year = request.form.get('completion_year')
        featured = 'featured' in request.form
        
        main_image = request.files.get('main_image')
        if main_image:
            filename = secure_filename(main_image.filename)
            main_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            project = Project(
                title=title,
                description=description,
                main_image=filename,
                category_id=category_id,
                location=location,
                area=area,
                completion_year=completion_year,
                featured=featured
            )
            db.session.add(project)
            db.session.commit()
            
            additional_images = request.files.getlist('additional_images')
            for image in additional_images:
                if image and image.filename:
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    project_image = ProjectImage(project_id=project.id, image_path=filename)
                    db.session.add(project_image)
            
            db.session.commit()
            flash('تم إضافة المشروع بنجاح!', 'success')
            return redirect(url_for('admin'))
    
    categories = Category.query.all()
    return render_template('add_project.html', categories=categories)


@app.route('/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        category_name = request.form['name']
        new_category = Category(name=category_name)
        db.session.add(new_category)
        db.session.commit()
        flash('تم إضافة التصنيف بنجاح!', 'success')
        return redirect(url_for('add_category'))  # Redirect to the same page or to another page
    return render_template('add_category.html')

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def update_settings():
    settings = SiteSettings.query.first()
    if request.method == 'POST':
        # تحديث اللون الأساسي
        settings.primary_color = request.form.get('primary_color')
        
        # معالجة تحميل الشعار
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file:
                logo_filename = secure_filename(logo_file.filename)
                logo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], logo_filename))
                settings.logo = logo_filename  # تأكد من وجود حقل logo في نموذج SiteSettings

        db.session.commit()
        print(f"تم حفظ اللون الجديد: {settings.primary_color}")  # تحقق من اللون المحفوظ
        flash('تم تحديث الإعدادات بنجاح!', 'success')
        return redirect(url_for('update_settings'))
    
    return render_template('settings.html', settings=settings)
    
@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def settings():
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings()
        db.session.add(settings)
        db.session.commit()
    
    if request.method == 'POST':
        settings.intro_text = request.form.get('intro_text')
        settings.phone_number = request.form.get('phone_number')
        settings.whatsapp_number = request.form.get('whatsapp_number')
        settings.facebook_url = request.form.get('facebook_url')
        settings.twitter_url = request.form.get('twitter_url')
        settings.instagram_url = request.form.get('instagram_url')
        settings.linkedin_url = request.form.get('linkedin_url')
        settings.hero_title = request.form.get('hero_title')
        settings.hero_subtitle = request.form.get('hero_subtitle')
        settings.service1_title = request.form.get('service1_title')
        settings.service1_description = request.form.get('service1_description')
        settings.service1_icon = request.form.get('service1_icon')
        settings.service2_title = request.form.get('service2_title')
        settings.service2_description = request.form.get('service2_description')
        settings.service2_icon = request.form.get('service2_icon')
        settings.service3_title = request.form.get('service3_title')
        settings.service3_description = request.form.get('service3_description')
        settings.service3_icon = request.form.get('service3_icon')
        settings.stats_projects = request.form.get('stats_projects')
        settings.stats_experience = request.form.get('stats_experience')
        settings.stats_clients = request.form.get('stats_clients')
        settings.stats_employees = request.form.get('stats_employees')
        settings.show_testimonials = 'show_testimonials' in request.form
        settings.testimonial1_name = request.form.get('testimonial1_name')
        settings.testimonial1_position = request.form.get('testimonial1_position')
        settings.testimonial1_text = request.form.get('testimonial1_text')
        settings.testimonial2_name = request.form.get('testimonial2_name')
        settings.testimonial2_position = request.form.get('testimonial2_position')
        settings.testimonial2_text = request.form.get('testimonial2_text')
        settings.testimonial3_name = request.form.get('testimonial3_name')
        settings.testimonial3_position = request.form.get('testimonial3_position')
        settings.testimonial3_text = request.form.get('testimonial3_text')
        settings.cta_title = request.form.get('cta_title')
        settings.cta_subtitle = request.form.get('cta_subtitle')
        
        logo = request.files.get('logo')
        if logo:
            filename = secure_filename(logo.filename)
            logo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            settings.logo_path = filename
        
        hero_image = request.files.get('hero_image')
        if hero_image:
            filename = secure_filename(hero_image.filename)
            hero_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            settings.hero_image = filename
        
        stats_image = request.files.get('stats_image')
        if stats_image:
            filename = secure_filename(stats_image.filename)
            stats_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            settings.stats_image = filename
        
        testimonial1_image = request.files.get('testimonial1_image')
        if testimonial1_image:
            filename = secure_filename(testimonial1_image.filename)
            testimonial1_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            settings.testimonial1_image = filename
        
        testimonial2_image = request.files.get('testimonial2_image')
        if testimonial2_image:
            filename = secure_filename(testimonial2_image.filename)
            testimonial2_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            settings.testimonial2_image = filename
        
        testimonial3_image = request.files.get('testimonial3_image')
        if testimonial3_image:
            filename = secure_filename(testimonial3_image.filename)
            testimonial3_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            settings.testimonial3_image = filename
        
        db.session.commit()
        flash('تم تحديث الإعدادات بنجاح!', 'success')
        return redirect(url_for('admin'))
    
    return render_template('admin.html', settings=settings)

@app.route('/admin/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form.get('name')
            name_ar = request.form.get('name_ar')
            category = Category(name=name, name_ar=name_ar)
            db.session.add(category)
        elif action == 'edit':
            category_id = request.form.get('category_id')
            category = Category.query.get_or_404(category_id)
            category.name = request.form.get('name')
            category.name_ar = request.form.get('name_ar')
        elif action == 'delete':
            category_id = request.form.get('category_id')
            category = Category.query.get_or_404(category_id)
            db.session.delete(category)
        
        db.session.commit()
        flash('تم تحديث التصنيفات بنجاح', 'success')
        return redirect(url_for('manage_categories'))
    
    categories = Category.query.all()
    return render_template('manage_categories.html', categories=categories)



@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول لهذه الصفحة', 'error')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            username = request.form.get('username')
            password = request.form.get('password')
            is_admin = 'is_admin' in request.form
            
            if User.query.filter_by(username=username).first():
                flash('اسم المستخدم موجود مسبقاً', 'error')
            else:
                user = User(username=username, is_admin=is_admin)
                user.password_hash = generate_password_hash(password)
                db.session.add(user)
                db.session.commit()
                flash('تم إضافة المستخدم بنجاح', 'success')
        
        elif action == 'edit':
            user_id = request.form.get('user_id')
            user = User.query.get_or_404(user_id)
            user.is_admin = 'is_admin' in request.form
            new_password = request.form.get('password')
            if new_password:
                user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash('تم تحديث بيانات المستخدم بنجاح', 'success')
        
        elif action == 'delete':
            user_id = request.form.get('user_id')
            if int(user_id) == current_user.id:
                flash('لا يمكنك حذف حسابك الحالي', 'error')
            else:
                user = User.query.get_or_404(user_id)
                db.session.delete(user)
                db.session.commit()
                flash('تم حذف المستخدم بنجاح', 'success')
        
        return redirect(url_for('manage_users'))
    
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@app.route('/admin/contact-requests')
@login_required
def admin_contact_requests():
    if not current_user.is_admin:
        abort(403)
    requests = ContactRequest.query.order_by(ContactRequest.created_at.desc()).all()
    return render_template('admin/contact_requests.html', requests=requests)


@app.route('/admin/contact-request/<int:request_id>', methods=['POST'])
@login_required
def update_contact_request(request_id):
    contact_request = ContactRequest.query.get_or_404(request_id)
    status = request.form.get('status')  # الحصول على الحالة من النموذج

    if status not in ['new', 'read', 'responded']:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400

    contact_request.status = status
    db.session.commit()
    flash('تم تحديث حالة الرسالة بنجاح!', 'success')
    return redirect(url_for('admin_contact_requests'))

@app.route('/admin/manage_users', methods=['GET', 'POST'])
@login_required
def manage_admins():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        # إضافة مشرف جديد
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        new_admin = User(username=username, email=email)
        new_admin.set_password(password)
        new_admin.is_admin = True  # تأكد من أن هذه السطر موجود
        db.session.add(new_admin)
        db.session.commit()
        flash('تم إضافة مشرف جديد بنجاح!', 'success')
        return redirect(url_for('manage_admins'))

    admins = User.query.filter_by(is_admin=True).all()
    return render_template('admin/manage_admins.html', admins=admins)

@app.route('/admin/update_admin', methods=['POST'])
@login_required
def update_admin():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))

    admin_id = request.form['admin_id']
    new_email = request.form.get('new_email')
    new_password = request.form.get('new_password')

    admin = User.query.get_or_404(admin_id)
    if new_email:
        admin.email = new_email
    if new_password:
        admin.set_password(new_password)

    db.session.commit()
    flash('تم تحديث بيانات المشرف بنجاح!', 'success')
    return redirect(url_for('manage_admins'))


@app.route('/admin/add_admin', methods=['GET', 'POST'])
@login_required
def add_admin():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # تحقق مما إذا كان المشرف موجودًا
        admin_id = request.form.get('admin_id')
        if admin_id:
            admin = User.query.get_or_404(admin_id)
            admin.username = username
            admin.email = email
            if password:  # تحديث كلمة المرور إذا تم توفيرها
                admin.set_password(password)
            flash('تم تحديث بيانات المشرف بنجاح!', 'success')
        else:
            # إضافة مشرف جديد
            admin = User(username=username, email=email)
            admin.set_password(password)
            admin.is_admin = True
            db.session.add(admin)
            flash('تم إضافة مشرف جديد بنجاح!', 'success')
        
        db.session.commit()
        return redirect(url_for('manage_users'))
    
    return render_template('add_admin.html')

@app.route('/admin/delete_admin/<int:admin_id>', methods=['POST'])
@login_required
def delete_admin(admin_id):
    admin = User.query.get_or_404(admin_id)
    db.session.delete(admin)
    db.session.commit()
    flash('تم حذف المشرف بنجاح!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/pages')
@login_required
def admin_pages():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
    
    # Get all page contents grouped by page
    pages = {}
    contents = PageContent.query.order_by(PageContent.page, PageContent.section).all()
    
    for content in contents:
        if content.page not in pages:
            pages[content.page] = []
        pages[content.page].append(content)
    
    return render_template('admin/page_content.html', pages=pages)

@app.route('/admin/pages/add', methods=['POST'])
@login_required
def add_page_content():
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'غير مصرح لك بالوصول'})
    
    page = request.form.get('page')
    section = request.form.get('section')
    content = request.form.get('content')
    content_type = request.form.get('content_type', 'text')
    
    if not all([page, section, content]):
        return jsonify({'success': False, 'message': 'جميع الحقول مطلوبة'})
    
    try:
        new_content = PageContent(
            page=page,
            section=section,
            content=content,
            content_type=content_type
        )
        db.session.add(new_content)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/pages/<int:content_id>')
@login_required
def get_page_content(content_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'غير مصرح لك بالوصول'})
    
    content = PageContent.query.get_or_404(content_id)
    return jsonify({
        'id': content.id,
        'page': content.page,
        'section': content.section,
        'content': content.content,
        'content_type': content.content_type
    })

@app.route('/admin/pages/<int:content_id>/update', methods=['POST'])
@login_required
def update_page_content(content_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'غير مصرح لك بالوصول'})
    
    content = PageContent.query.get_or_404(content_id)
    
    try:
        content.page = request.form.get('page', content.page)
        content.section = request.form.get('section', content.section)
        content.content = request.form.get('content', content.content)
        content.content_type = request.form.get('content_type', content.content_type)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/pages/<int:content_id>/delete', methods=['POST'])
@login_required
def delete_page_content(content_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'غير مصرح لك بالوصول'})
    
    content = PageContent.query.get_or_404(content_id)
    
    try:
        db.session.delete(content)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/about')
def about():
    settings = SiteSettings.query.first()
    return render_template('about.html', settings=settings)

@app.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    categories = Category.query.all()
    
    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.category_id = request.form.get('category_id')
        project.featured = 'featured' in request.form
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                project.main_image = filename

        db.session.commit()
        flash('تم تحديث المشروع بنجاح', 'success')
        return redirect(url_for('admin'))
        
    return render_template('edit_project.html', project=project, categories=categories)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    
    # Get statistics
    new_requests_count = ContactRequest.query.filter_by(status='new').count()
    projects_count = Project.query.count()
    pages_count = len(set([content.page for content in PageContent.query.all()]))
    
    # Get recent contact requests
    recent_requests = ContactRequest.query.order_by(ContactRequest.created_at.desc()).limit(5).all()
    
    # Get recent activities
    recent_activities = []
    
    # Add recent contact requests to activities
    for req in ContactRequest.query.order_by(ContactRequest.created_at.desc()).limit(3):
        recent_activities.append({
            'title': 'طلب اتصال جديد',
            'description': f'تم استلام طلب اتصال من {req.name}',
            'timestamp': req.created_at
        })
    
    # Add recent content updates to activities
    for content in PageContent.query.order_by(PageContent.last_updated.desc()).limit(3):
        recent_activities.append({
            'title': 'تحديث محتوى',
            'description': f'تم تحديث محتوى صفحة {content.page} - قسم {content.section}',
            'timestamp': content.last_updated
        })
    
    # Sort activities by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = recent_activities[:5]
    
    return render_template('admin/dashboard.html',
                         new_requests_count=new_requests_count,
                         projects_count=projects_count,
                         pages_count=pages_count,
                         recent_requests=recent_requests,
                         recent_activities=recent_activities)

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if not current_user.is_admin:
        abort(403)
    
    if request.method == 'POST':
        # Update site settings
        settings = SiteSettings.query.first()
        if not settings:
            settings = SiteSettings()
            db.session.add(settings)
        
        settings.site_name = request.form.get('site_name')
        settings.site_description = request.form.get('site_description')
        settings.contact_email = request.form.get('contact_email')
        settings.contact_phone = request.form.get('contact_phone')
        settings.address = request.form.get('address')
        
        # Handle logo upload
        if 'logo' in request.files:
            file = request.files['logo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                settings.logo = filename
        
        db.session.commit()
        flash('تم تحديث الإعدادات بنجاح', 'success')
        return redirect(url_for('admin_settings'))
    
    settings = SiteSettings.query.first()
    return render_template('admin/settings.html', settings=settings)

@app.route('/admin/projects')
@login_required
def admin_projects():
    if not current_user.is_admin:
        abort(403)
    projects = Project.query.all()
    categories = Category.query.all()
    return render_template('admin/projects.html', projects=projects, categories=categories)



@app.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    category = Category.query.get_or_404(category_id)
    
    # Check if category has projects
    if category.projects:
        return jsonify({
            'success': False, 
            'message': 'لا يمكن حذف التصنيف لأنه يحتوي على مشاريع'
        }), 400
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'success': True})
@app.route('/admin/delete_contact_request/<int:request_id>', methods=['POST'])
@login_required
def delete_contact_request(request_id):
    contact_request = ContactRequest.query.get_or_404(request_id)
    db.session.delete(contact_request)
    db.session.commit()
    flash('تم حذف الرسالة بنجاح!', 'success')
    return redirect(url_for('admin_contact_requests'))



@app.cli.command('create-admin')
@click.argument('username')
@click.argument('password')
@click.argument('email')
def create_admin(username, password, email):
    """Create a new admin user."""
    admin = User(username=username, email=email)  # تأكد من أن البريد الإلكتروني يتم تمريره هنا
    admin.set_password(password)
    admin.is_admin = True
    db.session.add(admin)
    db.session.commit()
    print(f'Admin user {username} created successfully.')
    
    
if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        db.create_all()
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        # Create default settings if not exists
        settings = SiteSettings.query.first()
        if not settings:
            settings = SiteSettings()
            db.session.add(settings)
            db.session.commit()
    
    app.run(debug=True)


@app.route('/admin/edit_admin/<int:admin_id>', methods=['GET', 'POST'])
@login_required
def edit_admin(admin_id):
    admin = User.query.get_or_404(admin_id)
    if request.method == 'POST':
        admin.username = request.form['username']
        admin.email = request.form['email']
        if request.form['password']:
            admin.set_password(request.form['password'])  # تحديث كلمة المرور إذا تم توفيرها
        db.session.commit()
        flash('تم تحديث بيانات المشرف بنجاح!', 'success')
        return redirect(url_for('manage_users'))
    return render_template('edit_admin.html', admin=admin)