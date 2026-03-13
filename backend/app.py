import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models import db, User, Subject, SchoolSettings
from config import config

# Complete subject list — Oguaa SHS Technical School 2025/26
DEFAULT_SUBJECTS = [
    "ENGLISH LANG",
    "GENERAL MATHS",
    "GENERAL SCIENCE",
    "SOCIAL STUDIES",
    "ADD MATH",
    "AGRICULTURE",
    "ANIMAL HUSBANDRY",
    "APPLIED ELECTRICITY",
    "ART FOUNDATION",
    "ART STUDIO",
    "AUTO MECHANICS",
    "AUTOMOBILE",
    "BC & WOOD",
    "BIOLOGY",
    "BUILDING CONSTRUCTION",
    "BUSINESS MANAGEMENT",
    "CERAMICS",
    "CHEMISTRY",
    "CHRISTIAN REL STD",
    "CLOTHING AND TEXTILES",
    "COMPUTER SCIENCE",
    "COST ACCOUNTING",
    "D.C.T",
    "ECONOMICS",
    "ELECTRICAL & ELECTRONICS",
    "FANTE",
    "FINANCIAL ACCOUNTING",
    "FOOD AND NUTRITION",
    "FRENCH",
    "GENERAL AGRIC",
    "GEOGRAPHY",
    "GKA",
    "GOVERNMENT",
    "GRAPHIC DESIGN",
    "HISTORY",
    "INFO COM TECH (ICT)",
    "JEWELLERY",
    "LITERATURE IN ENGLISH",
    "MANAGEMENT IN LIVING",
    "METALWORK",
    "PEH ELECTIVE",
    "PERFORMING ARTS",
    "PHYSICS",
    "PICTURE MAKING",
    "TECHNICAL DRAWING",
    "WOODWORK",
]


def create_app(env=None):
    app = Flask(__name__)
    env = env or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config.get(env, config['default']))

    db.init_app(app)
    JWTManager(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Blueprints ────────────────────────────────────────────────────────────
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.coordinator import coordinator_bp
    from routes.supervisor import supervisor_bp

    app.register_blueprint(auth_bp,         url_prefix='/api/auth')
    app.register_blueprint(admin_bp,        url_prefix='/api/admin')
    app.register_blueprint(coordinator_bp,  url_prefix='/api/coordinator')
    app.register_blueprint(supervisor_bp,   url_prefix='/api/supervisor')

    # ── CLI: flask init-db ────────────────────────────────────────────────────
    @app.cli.command('init-db')
    def init_db():
        db.create_all()
        print('✓ Tables created')

        # Default admin
        if not User.query.filter_by(role='admin').first():
            admin = User(
                username='admin',
                email='admin@school.edu.gh',
                role='admin',
                full_name='System Administrator'
            )
            admin.set_password('Admin@1234')
            db.session.add(admin)
            print('✓ Default admin → username: admin | password: Admin@1234')

        # Seed subjects
        added = 0
        for name in DEFAULT_SUBJECTS:
            if not Subject.query.filter_by(subject_name=name).first():
                db.session.add(Subject(subject_name=name))
                added += 1
        print(f'✓ Subjects: {added} new, {len(DEFAULT_SUBJECTS) - added} already existed')

        # Default school settings
        if not SchoolSettings.query.first():
            db.session.add(SchoolSettings(
                school_name='Your School',
                school_short='ASMaP School',
                school_motto='Excellence in Education',
                normal_start='07:30',
                extended_start='15:30',
            ))
            print('✓ Default school settings created')

        db.session.commit()
        print('\n✅ ASMaP database initialized successfully')
        print('   ⚠  Change the admin password after first login!\n')

    # ── CLI: flask migrate-v11 ────────────────────────────────────────────────
    @app.cli.command('migrate-v11')
    def migrate_v11():
        """Safe migration v1.1: adds teacher_subjects table + period column."""
        import sqlalchemy as sa
        engine = db.engine

        with engine.connect() as conn:
            conn.execute(sa.text("""
                CREATE TABLE IF NOT EXISTS teacher_subjects (
                    teacher_id INTEGER NOT NULL,
                    subject_id INTEGER NOT NULL,
                    PRIMARY KEY (teacher_id, subject_id),
                    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
                )
            """))
            print("✓ teacher_subjects table ready")

            try:
                conn.execute(sa.text("""
                    INSERT INTO teacher_subjects (teacher_id, subject_id)
                    SELECT id, subject_id FROM teachers
                    WHERE subject_id IS NOT NULL
                    ON CONFLICT DO NOTHING
                """))
                print("✓ Existing teacher-subject links migrated")
            except Exception as e:
                print(f"⚠ Could not seed teacher_subjects: {e}")

            try:
                conn.execute(sa.text(
                    "ALTER TABLE monitoring_records ADD COLUMN period VARCHAR(60)"
                ))
                print("✓ Added 'period' column to monitoring_records")
            except Exception:
                print("✓ 'period' column already exists — skipped")

            conn.commit()

        print("\n✅ Migration v1.1 complete!")
        print("   No existing data was changed or deleted.")

    # ── Health check ──────────────────────────────────────────────────────────
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'system': 'ASMaP', 'version': '1.1'}

    return app


# ── Standalone run ────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
