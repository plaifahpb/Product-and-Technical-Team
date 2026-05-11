
import os, sqlite3, json, uuid, hashlib, binascii, io, csv
from datetime import datetime, date
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response, send_file

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(APP_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'task_tracker.db')
MASTER_PATH = os.path.join(DATA_DIR, 'master.json')
SPARE_UPLOAD_DIR = os.path.join(APP_DIR, 'static', 'spare_parts')
TASK_UPLOAD_DIR = os.path.join(APP_DIR, 'static', 'task_images')
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp', 'svg'}

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret-key-in-env')
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    MAX_CONTENT_LENGTH=25 * 1024 * 1024
)

STATUS_LIST = ['Not Started', 'In Progress', 'Completed', 'On Hold', 'Cancelled']
PRIORITY_LIST = ['Low', 'Normal', 'High', 'Critical']
CASE_CLASSIFICATION_LIST = ['Hardware', 'Software', 'Installation', 'Calibration', 'Training', 'User Error', 'Data Processing', 'Unknown']
CATEGORY_LIST = ['01_Equipment Setup','02_Training & Guidance','03_Software Support','04_Hardware Support','05_Data Processing','06_Manual','07_Other']
PURCHASE_SOURCE_LIST = ['OEM Direct', 'Local Supplier', 'Distributor', 'Internal Fabrication', 'RMA Replacement', 'Not Specified']

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def ensure_production_database():
    """Create required production tables/users when /app/data is empty on cloud disk."""
    os.makedirs(DATA_DIR, exist_ok=True)
    con = db()
    con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            display_name TEXT
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_code TEXT,
            task_description TEXT,
            category TEXT,
            owner TEXT,
            priority TEXT,
            status TEXT,
            due_date TEXT,
            important INTEGER DEFAULT 0,
            urgent INTEGER DEFAULT 0,
            note TEXT,
            sub_product_id TEXT,
            customer TEXT,
            open_date TEXT,
            closed_date TEXT,
            kpi_result TEXT,
            ms_team TEXT,
            day_remaining_auto TEXT,
            due_bucket TEXT,
            problem_summary TEXT,
            root_cause TEXT,
            troubleshooting_process TEXT,
            solution_resolution TEXT,
            preventive_action TEXT,
            case_classification TEXT,
            repeated_issue INTEGER DEFAULT 0,
            knowledge_tags TEXT,
            evidence_link TEXT
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            action TEXT,
            field_name TEXT,
            old_value TEXT,
            new_value TEXT,
            actor TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS product_assets (
            product_id TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            product_code TEXT,
            description TEXT,
            status TEXT DEFAULT 'Active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS product_components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL,
            sub_product_id TEXT NOT NULL,
            component_name TEXT,
            part_type TEXT,
            legacy_equipment_name TEXT,
            sort_order INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(product_id, sub_product_id)
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS spare_parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_code TEXT,
            product_id TEXT,
            product_name TEXT,
            component_id INTEGER,
            sub_product_id TEXT,
            sn TEXT,
            image_link TEXT,
            name_product TEXT,
            part_type TEXT,
            equipment_name TEXT,
            warranty TEXT,
            purchase_id TEXT,
            purchase_source TEXT DEFAULT 'Not Specified',
            supplier_name TEXT,
            po_number TEXT,
            country TEXT,
            warranty_expiry TEXT,
            qty INTEGER DEFAULT 1,
            status TEXT DEFAULT 'Active',
            remark TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS task_spare_parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            spare_part_id INTEGER NOT NULL,
            qty INTEGER DEFAULT 1,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS task_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            caption TEXT,
            created_by TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Seed production users if empty
    count = con.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    if count == 0:
        con.executemany(
            "INSERT INTO users(username,password,role,display_name) VALUES (?,?,?,?)",
            [
                ("SBDTP", make_password_hash("SBDTP"), "Admin", "SBDTP Admin"),
                ("SBD_Internal", make_password_hash("SBD_Internal"), "Staff", "SBD Internal Team"),
                ("iNFRA", make_password_hash("iNFRA"), "Viewer", "iNFRA Viewer"),
            ]
        )
    con.commit()
    con.close()



def load_master():
    if os.path.exists(MASTER_PATH):
        with open(MASTER_PATH, encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_master(master):
    os.makedirs(os.path.dirname(MASTER_PATH), exist_ok=True)
    with open(MASTER_PATH, 'w', encoding='utf-8') as f:
        json.dump(master, f, ensure_ascii=False, indent=2)

def add_master_value(key, value):
    value = (value or '').strip()
    if not value:
        return False
    master = load_master()
    values = master.setdefault(key, [])
    if value not in values:
        values.append(value)
        values.sort(key=lambda x: str(x).lower())
        save_master(master)
        return True
    return False



def make_password_hash(password):
    salt = "sbdtp_static_salt_v1"
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 120000)
    return "pbkdf2_sha256$" + salt + "$" + binascii.hexlify(dk).decode()


def verify_password(stored_password, provided_password):
    stored_password = stored_password or ''
    if stored_password.startswith('pbkdf2_sha256$'):
        try:
            _, salt, hashed = stored_password.split('$', 2)
            dk = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 120000)
            return binascii.hexlify(dk).decode() == hashed
        except Exception:
            return False
    # Backward-compatible fallback for old local/demo database rows.
    return stored_password == provided_password

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper

def role_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if session.get('role') not in roles:
                flash('คุณไม่มีสิทธิ์ดำเนินการนี้', 'danger')
                return redirect(url_for('dashboard'))
            return fn(*args, **kwargs)
        return wrapper
    return deco

def row_to_dict(row):
    return dict(row) if row else None

def filtered_query(args):
    where=[]; params=[]
    q=args.get('q','').strip()
    if q:
        where.append('(task_description LIKE ? OR note LIKE ? OR customer LIKE ? OR sub_product_id LIKE ?)')
        params += [f'%{q}%']*4
    for col in ['owner','status','priority','customer','category']:
        val=args.get(col,'').strip()
        if val:
            where.append(f'{col} = ?'); params.append(val)
    product=args.get('product','').strip()
    if product:
        where.append('sub_product_id = ?'); params.append(product)
    start=args.get('start','').strip(); end=args.get('end','').strip()
    if start: where.append('due_date >= ?'); params.append(start)
    if end: where.append('due_date <= ?'); params.append(end)
    sql='SELECT * FROM tasks'
    if where: sql += ' WHERE ' + ' AND '.join(where)
    sql += ' ORDER BY CASE WHEN status="Completed" THEN 1 ELSE 0 END, due_date ASC, priority DESC'
    return sql, params


def month_options():
    con=db()
    rows=con.execute("""
        SELECT DISTINCT substr(open_date,1,7) AS month_key
        FROM tasks
        WHERE open_date IS NOT NULL AND open_date != ''
        ORDER BY month_key DESC
    """).fetchall()
    con.close()
    return [r['month_key'] for r in rows if r['month_key']]

def monthly_kpi(month_key=None):
    months = month_options()
    if not month_key:
        month_key = datetime.now().strftime('%Y-%m')
        if month_key not in months and months:
            month_key = months[0]
    con=db()
    opened_rows=[row_to_dict(r) for r in con.execute("""
        SELECT * FROM tasks
        WHERE open_date IS NOT NULL AND open_date != ''
          AND substr(open_date,1,7)=?
    """,(month_key,)).fetchall()]
    closed_in_month=0
    for r in opened_rows:
        od=(r.get('open_date') or '')[:7]
        cd=(r.get('closed_date') or '')[:7]
        if od == month_key and cd == month_key and str(r.get('status')).lower() == 'completed':
            closed_in_month += 1
    opened=len(opened_rows)
    rate=round(closed_in_month/opened*100,2) if opened else 0
    result='PASS' if opened and rate >= 95 else 'FAIL'
    product_rows=con.execute("""
        SELECT COALESCE(NULLIF(TRIM(sub_product_id),''),'Unknown') AS product,
               COUNT(*) AS opened,
               SUM(CASE WHEN status='Completed' AND closed_date IS NOT NULL AND substr(closed_date,1,7)=substr(open_date,1,7) THEN 1 ELSE 0 END) AS closed_in_month,
               SUM(CASE WHEN NOT (status='Completed' AND closed_date IS NOT NULL AND substr(closed_date,1,7)=substr(open_date,1,7)) THEN 1 ELSE 0 END) AS not_closed_in_month
        FROM tasks
        WHERE open_date IS NOT NULL AND open_date != '' AND substr(open_date,1,7)=?
        GROUP BY product
        ORDER BY not_closed_in_month DESC, opened DESC
        LIMIT 15
    """,(month_key,)).fetchall()
    year=(month_key[:4] if month_key else datetime.now().strftime('%Y'))
    product_year=con.execute("""
        SELECT COALESCE(NULLIF(TRIM(sub_product_id),''),'Unknown') AS product,
               COUNT(*) AS opened,
               SUM(CASE WHEN status='Completed' THEN 1 ELSE 0 END) AS completed,
               SUM(CASE WHEN status<>'Completed' OR status IS NULL THEN 1 ELSE 0 END) AS outstanding
        FROM tasks
        WHERE open_date IS NOT NULL AND open_date != '' AND substr(open_date,1,4)=?
        GROUP BY product
        ORDER BY opened DESC
        LIMIT 15
    """,(year,)).fetchall()
    con.close()
    return {
        'month_key': month_key, 'months': months, 'opened': opened,
        'closed_in_month': closed_in_month, 'rate': rate, 'result': result,
        'target': 95, 'product_rows':[dict(r) for r in product_rows],
        'product_year':[dict(r) for r in product_year], 'year': year
    }

def calculate_metrics(rows):
    today = date.today()
    total=len(rows)
    completed=sum(1 for r in rows if str(r['status']).lower()=='completed')
    in_progress=sum(1 for r in rows if str(r['status']).lower()=='in progress')
    not_started=sum(1 for r in rows if str(r['status']).lower()=='not started')
    overdue=0; due7=0; urgent=0; important=0
    for r in rows:
        if r['urgent']: urgent+=1
        if r['important']: important+=1
        if str(r['status']).lower()!='completed' and r['due_date']:
            try:
                dd=datetime.strptime(r['due_date'], '%Y-%m-%d').date()
                if dd < today: overdue += 1
                elif (dd-today).days <= 7: due7 += 1
            except Exception: pass
    return {
        'total': total, 'completed': completed, 'in_progress': in_progress, 'not_started': not_started,
        'outstanding': total-completed, 'overdue': overdue, 'due7': due7, 'urgent': urgent,
        'important': important, 'completion_rate': round((completed/total*100),1) if total else 0
    }

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username=request.form.get('username','').strip()
        password=request.form.get('password','').strip()
        con=db(); user=con.execute('SELECT * FROM users WHERE username=?',(username,)).fetchone(); con.close()
        if user and verify_password(user['password'], password):
            session['user']=user['username']; session['role']=user['role']; session['display_name']=user['display_name']
            return redirect(url_for('dashboard'))
        flash('Username หรือ Password ไม่ถูกต้อง', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    con=db(); sql,params=filtered_query(request.args); rows=[row_to_dict(r) for r in con.execute(sql,params).fetchall()]
    metrics=calculate_metrics(rows)
    # summaries
    status=dict(con.execute('SELECT COALESCE(status,"Unknown") s, COUNT(*) c FROM tasks GROUP BY s').fetchall())
    owner=dict(con.execute('SELECT COALESCE(owner,"Unknown") s, COUNT(*) c FROM tasks GROUP BY s ORDER BY c DESC LIMIT 15').fetchall())
    priority=dict(con.execute('SELECT COALESCE(priority,"Unknown") s, COUNT(*) c FROM tasks GROUP BY s').fetchall())
    customer=dict(con.execute('SELECT COALESCE(customer,"Unknown") s, COUNT(*) c FROM tasks GROUP BY s ORDER BY c DESC LIMIT 10').fetchall())
    upcoming=[row_to_dict(r) for r in con.execute('SELECT * FROM tasks WHERE status<>"Completed" AND due_date IS NOT NULL ORDER BY due_date LIMIT 8').fetchall()]
    con.close()
    kpi=monthly_kpi(request.args.get('kpi_month','').strip() or None)
    return render_template('dashboard.html', metrics=metrics, status=status, owner=owner, priority=priority, customer=customer, upcoming=upcoming, kpi=kpi)

@app.route('/tasks')
@login_required
def tasks():
    con=db(); sql,params=filtered_query(request.args); rows=[row_to_dict(r) for r in con.execute(sql,params).fetchall()]
    master=load_master(); con.close()
    return render_template('tasks.html', rows=rows, master=master, statuses=STATUS_LIST, priorities=PRIORITY_LIST, categories=CATEGORY_LIST)

@app.route('/tasks/new', methods=['GET','POST'])
@login_required
@role_required('Admin','Manager','Staff')
def task_new():
    master=load_master()
    if request.method=='POST':
        data=form_task()
        cols=','.join(data.keys()); qs=','.join(['?']*len(data))
        con=db(); cur=con.execute(f'INSERT INTO tasks ({cols}) VALUES ({qs})', list(data.values()))
        con.execute('INSERT INTO audit_log(task_id,action,actor,new_value) VALUES (?,?,?,?)',(cur.lastrowid,'CREATE',session.get('user'),json.dumps(data,ensure_ascii=False)))
        con.commit(); con.close(); flash('เพิ่ม Task สำเร็จ', 'success'); return redirect(url_for('tasks'))
    return render_template('task_form.html', item={}, master=master, statuses=STATUS_LIST, priorities=PRIORITY_LIST, categories=CATEGORY_LIST, classifications=CASE_CLASSIFICATION_LIST, mode='new')

@app.route('/tasks/<int:task_id>/edit', methods=['GET','POST'])
@login_required
@role_required('Admin','Manager','Staff')
def task_edit(task_id):
    con=db(); item=row_to_dict(con.execute('SELECT * FROM tasks WHERE id=?',(task_id,)).fetchone())
    if not item: con.close(); flash('ไม่พบ Task', 'danger'); return redirect(url_for('tasks'))
    if session.get('role')=='Staff' and item.get('owner') and item.get('owner') != session.get('display_name') and item.get('owner') != session.get('user'):
        # still allow because imported owner names may not match login; change here if strict owner-only editing required
        pass
    if request.method=='POST':
        data=form_task(); changes=[]
        for k,v in data.items():
            if str(item.get(k,'')) != str(v or ''):
                changes.append((task_id,'UPDATE',k,str(item.get(k,'')),str(v or ''),session.get('user')))
        sets=','.join([f'{k}=?' for k in data.keys()])
        con.execute(f'UPDATE tasks SET {sets} WHERE id=?', list(data.values())+[task_id])
        con.executemany('INSERT INTO audit_log(task_id,action,field_name,old_value,new_value,actor) VALUES (?,?,?,?,?,?)', changes)
        con.commit(); con.close(); flash('แก้ไข Task สำเร็จ', 'success'); return redirect(url_for('tasks'))
    con.close(); return render_template('task_form.html', item=item, master=load_master(), statuses=STATUS_LIST, priorities=PRIORITY_LIST, categories=CATEGORY_LIST, classifications=CASE_CLASSIFICATION_LIST, mode='edit')

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
@role_required('Admin','Manager')
def task_delete(task_id):
    con=db(); con.execute('DELETE FROM tasks WHERE id=?',(task_id,)); con.execute('INSERT INTO audit_log(task_id,action,actor) VALUES (?,?,?)',(task_id,'DELETE',session.get('user'))); con.commit(); con.close()
    flash('ลบ Task แล้ว', 'warning'); return redirect(url_for('tasks'))


def generate_case_code(open_date=None):
    year = (open_date or datetime.now().strftime('%Y-%m-%d'))[:4]
    if not year.isdigit():
        year = datetime.now().strftime('%Y')
    con=db()
    row=con.execute("SELECT COUNT(*) AS c FROM tasks WHERE case_code LIKE ?", (f"TK-{year}-%",)).fetchone()
    con.close()
    return f"TK-{year}-{(row['c'] or 0)+1:04d}"


def form_task():
    fields=[
        'case_code','task_description','category','owner','priority','status','due_date','important','urgent','note',
        'sub_product_id','customer','open_date','closed_date','kpi_result','ms_team',
        'problem_summary','root_cause','troubleshooting_process','solution_resolution',
        'preventive_action','case_classification','knowledge_tags','evidence_link'
    ]
    data={}
    for f in fields:
        if f in ['important','urgent']:
            data[f]=1 if request.form.get(f) else 0
        else:
            data[f]=request.form.get(f) or None
    data['repeated_issue']=1 if request.form.get('repeated_issue') else 0
    if not data.get('case_code'):
        data['case_code']=generate_case_code(data.get('open_date'))

    # compatible columns from Excel
    if not data.get('kpi_result'):
        data['kpi_result']='Closed in-month' if data.get('status')=='Completed' else 'Not closed in-month'
    try:
        if data.get('status')=='Completed': data['day_remaining_auto']='Completed'
        elif data.get('due_date'):
            dd=datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            data['day_remaining_auto']=(dd-date.today()).days
        else: data['day_remaining_auto']=None
    except Exception: data['day_remaining_auto']=None
    data['due_bucket']='Completed' if data.get('status')=='Completed' else None
    return data

@app.route('/tasks/<int:task_id>')
@login_required
def task_detail(task_id):
    con=db()
    item=row_to_dict(con.execute('SELECT * FROM tasks WHERE id=?',(task_id,)).fetchone())
    if not item:
        con.close()
        flash('ไม่พบ Task', 'danger')
        return redirect(url_for('tasks'))

    spare_used=[row_to_dict(r) for r in con.execute("""
        SELECT tsp.*, sp.asset_code, sp.name_product, sp.sn, sp.product_id, sp.sub_product_id, COALESCE(pa.product_name, sp.product_name, sp.product_id) AS product_name
        FROM task_spare_parts tsp
        JOIN spare_parts sp ON sp.id=tsp.spare_part_id
        LEFT JOIN product_assets pa ON pa.product_id=sp.product_id
        WHERE tsp.task_id=?
        ORDER BY tsp.created_at DESC
    """,(task_id,)).fetchall()]
    spare_options=[row_to_dict(r) for r in con.execute("""
        SELECT sp.id, sp.asset_code, sp.name_product, sp.sn, sp.product_id, sp.sub_product_id, COALESCE(pa.product_name, sp.product_name, sp.product_id) AS product_name
        FROM spare_parts sp
        LEFT JOIN product_assets pa ON pa.product_id=sp.product_id
        ORDER BY CAST(sp.product_id AS INTEGER), CAST(sp.sub_product_id AS INTEGER), sp.name_product
        LIMIT 1000
    """).fetchall()]
    task_images=[row_to_dict(r) for r in con.execute('SELECT * FROM task_images WHERE task_id=? ORDER BY created_at DESC',(task_id,)).fetchall()]
    con.close()
    return render_template('task_detail.html', item=item, spare_used=spare_used, spare_options=spare_options, task_images=task_images, classifications=CASE_CLASSIFICATION_LIST)

@app.route('/tasks/<int:task_id>/knowledge', methods=['POST'])
@login_required
@role_required('Admin','Manager','Staff')
def task_knowledge_update(task_id):
    fields=['problem_summary','root_cause','troubleshooting_process','solution_resolution','preventive_action','case_classification','knowledge_tags','evidence_link']
    data={f: request.form.get(f) or None for f in fields}
    data['repeated_issue']=1 if request.form.get('repeated_issue') else 0
    con=db()
    old=row_to_dict(con.execute('SELECT * FROM tasks WHERE id=?',(task_id,)).fetchone())
    if not old:
        con.close()
        flash('ไม่พบ Task', 'danger')
        return redirect(url_for('tasks'))
    sets=','.join([f'{k}=?' for k in data.keys()])
    con.execute(f'UPDATE tasks SET {sets} WHERE id=?', list(data.values())+[task_id])
    con.execute('INSERT INTO audit_log(task_id,action,field_name,old_value,new_value,actor) VALUES (?,?,?,?,?,?)',
                (task_id,'KNOWLEDGE_UPDATE','Case Knowledge',
                 json.dumps({k: old.get(k) for k in data.keys()},ensure_ascii=False),
                 json.dumps(data,ensure_ascii=False),session.get('user')))
    con.commit(); con.close()
    flash('บันทึก Case Knowledge สำเร็จ', 'success')
    return redirect(url_for('task_detail', task_id=task_id))

@app.route('/tasks/<int:task_id>/spare-used', methods=['POST'])
@login_required
@role_required('Admin','Manager','Staff')
def task_spare_used_add(task_id):
    spare_part_id=request.form.get('spare_part_id')
    qty=request.form.get('qty') or 1
    note=request.form.get('note') or None
    try:
        qty=int(qty)
    except Exception:
        qty=1
    if spare_part_id:
        con=db()
        con.execute('INSERT INTO task_spare_parts(task_id,spare_part_id,qty,note) VALUES (?,?,?,?)',(task_id,spare_part_id,qty,note))
        con.execute('INSERT INTO audit_log(task_id,action,field_name,new_value,actor) VALUES (?,?,?,?,?)',(task_id,'SPARE_USED_ADD','Spare Part Used',str(spare_part_id),session.get('user')))
        con.commit(); con.close()
        flash('เพิ่ม Spare Part Used สำเร็จ', 'success')
    return redirect(url_for('task_detail', task_id=task_id))

@app.route('/tasks/<int:task_id>/spare-used/<int:link_id>/delete', methods=['POST'])
@login_required
@role_required('Admin','Manager')
def task_spare_used_delete(task_id, link_id):
    con=db()
    con.execute('DELETE FROM task_spare_parts WHERE id=? AND task_id=?',(link_id,task_id))
    con.execute('INSERT INTO audit_log(task_id,action,field_name,old_value,actor) VALUES (?,?,?,?,?)',(task_id,'SPARE_USED_DELETE','Spare Part Used',str(link_id),session.get('user')))
    con.commit(); con.close()
    flash('ลบ Spare Part Used แล้ว', 'warning')
    return redirect(url_for('task_detail', task_id=task_id))


@app.route('/tasks/<int:task_id>/images', methods=['POST'])
@login_required
@role_required('Admin','Manager','Staff')
def task_image_upload(task_id):
    image_path = save_task_image(request.files.get('image_file'))
    caption = request.form.get('caption') or None
    if image_path:
        con=db()
        con.execute('INSERT INTO task_images(task_id,image_path,caption,created_by) VALUES (?,?,?,?)',
                    (task_id,image_path,caption,session.get('user')))
        con.execute('INSERT INTO audit_log(task_id,action,field_name,new_value,actor) VALUES (?,?,?,?,?)',
                    (task_id,'TASK_IMAGE_UPLOAD','Case Image',image_path,session.get('user')))
        con.commit(); con.close()
        flash('อัปโหลดรูปประกอบเคสสำเร็จ', 'success')
    return redirect(url_for('task_detail', task_id=task_id))

@app.route('/tasks/<int:task_id>/images/<int:image_id>/delete', methods=['POST'])
@login_required
@role_required('Admin','Manager')
def task_image_delete(task_id, image_id):
    con=db()
    img=row_to_dict(con.execute('SELECT * FROM task_images WHERE id=? AND task_id=?',(image_id,task_id)).fetchone())
    if img:
        con.execute('DELETE FROM task_images WHERE id=? AND task_id=?',(image_id,task_id))
        con.execute('INSERT INTO audit_log(task_id,action,field_name,old_value,actor) VALUES (?,?,?,?,?)',
                    (task_id,'TASK_IMAGE_DELETE','Case Image',img.get('image_path'),session.get('user')))
        con.commit()
    con.close()
    flash('ลบรูปประกอบเคสแล้ว', 'warning')
    return redirect(url_for('task_detail', task_id=task_id))


@app.route('/knowledge-base')
@login_required
def knowledge_base():
    q=request.args.get('q','').strip()
    product=request.args.get('product','').strip()
    classification=request.args.get('classification','').strip()
    where=["(problem_summary IS NOT NULL OR root_cause IS NOT NULL OR solution_resolution IS NOT NULL)"]
    params=[]
    if q:
        where.append("""(task_description LIKE ? OR problem_summary LIKE ? OR root_cause LIKE ? OR troubleshooting_process LIKE ? OR solution_resolution LIKE ? OR preventive_action LIKE ? OR knowledge_tags LIKE ?)""")
        params += [f'%{q}%']*7
    if product:
        where.append("sub_product_id=?"); params.append(product)
    if classification:
        where.append("case_classification=?"); params.append(classification)
    sql='SELECT * FROM tasks WHERE ' + ' AND '.join(where) + ' ORDER BY closed_date DESC, open_date DESC, id DESC'
    con=db()
    rows=[row_to_dict(r) for r in con.execute(sql,params).fetchall()]
    master=load_master()
    con.close()
    return render_template('knowledge_base.html', rows=rows, master=master, classifications=CASE_CLASSIFICATION_LIST)

@app.route('/calendar')
@login_required
def calendar():
    con=db(); rows=[row_to_dict(r) for r in con.execute('SELECT id, task_description, owner, status, priority, due_date, important, urgent FROM tasks WHERE due_date IS NOT NULL').fetchall()]; con.close()
    events=[]
    for r in rows:
        color = '#16a34a' if r['status']=='Completed' else '#dc2626' if r['urgent'] else '#2563eb' if r['status']=='In Progress' else '#f59e0b'
        events.append({'id':r['id'], 'title':r['task_description'], 'start':r['due_date'], 'color':color, 'extendedProps':r})
    return render_template('calendar.html', events=json.dumps(events, ensure_ascii=False))

@app.route('/analytics')
@login_required
def analytics():
    con=db()
    monthly_rows = con.execute('''
        SELECT substr(due_date, 1, 7) AS month_key, COUNT(*) AS total
        FROM tasks
        WHERE due_date IS NOT NULL AND due_date != ''
        GROUP BY month_key
        ORDER BY month_key DESC
        LIMIT 12
    ''').fetchall()
    monthly = {r['month_key']: r['total'] for r in reversed(monthly_rows)}

    rows = con.execute('''
        SELECT owner, status, COUNT(*) AS total
        FROM tasks
        GROUP BY owner, status
        ORDER BY owner
    ''').fetchall()
    con.close()

    owner_map = {}
    for r in rows:
        owner = r['owner'] or 'Unassigned'
        status = r['status'] or 'Unknown'
        owner_map.setdefault(owner, {'owner': owner})
        owner_map[owner][status] = r['total']
    owner_status = list(owner_map.values())
    kpi=monthly_kpi(request.args.get('kpi_month','').strip() or None)
    return render_template('analytics.html', monthly=monthly, owner_status=owner_status, kpi=kpi)


@app.route('/master/products', methods=['GET','POST'])
@login_required
@role_required('Admin','Manager')
def product_master():
    master = load_master()
    products = master.get('sup_product_id', [])
    if request.method == 'POST':
        value = request.form.get('product_name','').strip()
        if add_master_value('sup_product_id', value):
            con=db()
            con.execute('INSERT INTO audit_log(action,field_name,new_value,actor) VALUES (?,?,?,?)',('MASTER_CREATE','Product',value,session.get('user')))
            con.commit(); con.close()
            flash('เพิ่ม Product ใหม่สำเร็จ', 'success')
        else:
            flash('Product นี้มีอยู่แล้ว หรือยังไม่ได้กรอกชื่อ', 'warning')
        return redirect(url_for('product_master'))
    return render_template('product_master.html', products=products)

@app.route('/master/products/delete', methods=['POST'])
@login_required
@role_required('Admin','Manager')
def product_master_delete():
    value = request.form.get('product_name','').strip()
    master = load_master()
    products = master.get('sup_product_id', [])
    if value in products:
        products.remove(value)
        save_master(master)
        con=db()
        con.execute('INSERT INTO audit_log(action,field_name,old_value,actor) VALUES (?,?,?,?)',('MASTER_DELETE','Product',value,session.get('user')))
        con.commit(); con.close()
        flash('ลบ Product จาก Master แล้ว แต่ Task เดิมที่เคยใช้ Product นี้จะยังเก็บค่าเดิมไว้', 'warning')
    return redirect(url_for('product_master'))



def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def save_spare_image(file_obj):
    if not file_obj or not getattr(file_obj, 'filename', ''):
        return None
    if not allowed_image_file(file_obj.filename):
        flash('รองรับเฉพาะไฟล์รูปภาพ: png, jpg, jpeg, webp, gif, bmp, svg', 'danger')
        return None
    os.makedirs(SPARE_UPLOAD_DIR, exist_ok=True)
    ext = file_obj.filename.rsplit('.', 1)[1].lower()
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"
    full_path = os.path.join(SPARE_UPLOAD_DIR, filename)
    file_obj.save(full_path)
    return f"/static/spare_parts/{filename}"


def save_task_image(file_obj):
    if not file_obj or not getattr(file_obj, 'filename', ''):
        return None
    if not allowed_image_file(file_obj.filename):
        flash('รองรับเฉพาะไฟล์รูปภาพ: png, jpg, jpeg, webp, gif, bmp, svg', 'danger')
        return None
    os.makedirs(TASK_UPLOAD_DIR, exist_ok=True)
    ext = file_obj.filename.rsplit('.', 1)[1].lower()
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"
    full_path = os.path.join(TASK_UPLOAD_DIR, filename)
    file_obj.save(full_path)
    return f"/static/task_images/{filename}"

def spare_summary():
    con=db()
    total=con.execute('SELECT COUNT(*) c FROM spare_parts').fetchone()['c']
    products=con.execute("SELECT COUNT(DISTINCT COALESCE(NULLIF(TRIM(product_id),''),'Unknown')) c FROM spare_parts").fetchone()['c']
    components=con.execute("SELECT COUNT(DISTINCT component_id) c FROM spare_parts WHERE component_id IS NOT NULL").fetchone()['c']
    with_sn=con.execute("SELECT COUNT(*) c FROM spare_parts WHERE sn IS NOT NULL AND TRIM(sn)<>''").fetchone()['c']
    by_product=[dict(r) for r in con.execute("""
        SELECT COALESCE(pa.product_name, sp.product_name, sp.product_id, 'Unknown') AS label, COUNT(*) AS count
        FROM spare_parts sp
        LEFT JOIN product_assets pa ON pa.product_id = sp.product_id
        GROUP BY label ORDER BY count DESC LIMIT 20
    """).fetchall()]
    by_type=[dict(r) for r in con.execute("""
        SELECT COALESCE(NULLIF(TRIM(part_type),''),'Unknown') AS label, COUNT(*) AS count
        FROM spare_parts GROUP BY label ORDER BY count DESC LIMIT 20
    """).fetchall()]
    con.close()
    return {
        'total': total,
        'equipment': products,
        'part_types': components,
        'with_sn': with_sn,
        'without_sn': total - with_sn,
        'by_equipment': by_product,
        'by_type': by_type
    }

@app.route('/spare-parts')
@login_required
def spare_parts():
    q=request.args.get('q','').strip()
    product_id=request.args.get('product_id','').strip()
    part_type=request.args.get('part_type','').strip()
    where=[]; params=[]
    if q:
        where.append('(sp.asset_code LIKE ? OR sp.name_product LIKE ? OR sp.image_link LIKE ? OR sp.sn LIKE ? OR sp.purchase_id LIKE ? OR sp.po_number LIKE ? OR sp.supplier_name LIKE ? OR sp.sub_product_id LIKE ? OR pc.component_name LIKE ?)')
        params += [f'%{q}%']*9
    if product_id:
        where.append('sp.product_id = ?'); params.append(product_id)
    if part_type:
        where.append('sp.part_type = ?'); params.append(part_type)
    sql="""
        SELECT sp.*, COALESCE(pa.product_name, sp.product_name, sp.product_id, 'Unknown') AS product_display,
               pc.component_name AS component_display
        FROM spare_parts sp
        LEFT JOIN product_assets pa ON pa.product_id = sp.product_id
        LEFT JOIN product_components pc ON pc.id = sp.component_id
    """
    if where:
        sql += ' WHERE ' + ' AND '.join(where)
    sql += ' ORDER BY CAST(sp.product_id AS INTEGER), CAST(sp.sub_product_id AS INTEGER), sp.name_product'
    con=db()
    rows=[row_to_dict(r) for r in con.execute(sql,params).fetchall()]
    products=[dict(r) for r in con.execute("SELECT product_id, product_name FROM product_assets ORDER BY CAST(product_id AS INTEGER), product_name").fetchall()]
    part_types=[r['v'] for r in con.execute("SELECT DISTINCT part_type v FROM spare_parts WHERE part_type IS NOT NULL AND TRIM(part_type)<>'' ORDER BY v").fetchall()]
    summary=spare_summary()
    con.close()
    return render_template('spare_parts.html', rows=rows, products=products, part_types=part_types, summary=summary)

@app.route('/spare-parts/new', methods=['GET','POST'])
@login_required
@role_required('Admin','Manager','Staff')
def spare_part_new():
    if request.method=='POST':
        data=form_spare_part()
        con=db()
        cur=con.execute("""
            INSERT INTO spare_parts(asset_code, product_id, sub_product_id, sn, image_link, name_product, part_type, equipment_name, warranty, purchase_id, purchase_source, supplier_name, po_number, country, warranty_expiry, qty, status, remark)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (data['asset_code'],data['product_id'],data['sub_product_id'],data['sn'],data['image_link'],data['name_product'],data['part_type'],data['equipment_name'],data['warranty'],data['purchase_id'],data['purchase_source'],data['supplier_name'],data['po_number'],data['country'],data['warranty_expiry'],data['qty'],data['status'],data['remark']))
        con.execute('INSERT INTO audit_log(action,field_name,new_value,actor) VALUES (?,?,?,?)',('SPARE_CREATE','Spare Part',json.dumps(data,ensure_ascii=False),session.get('user')))
        con.commit(); con.close()
        flash('เพิ่ม Spare Part สำเร็จ', 'success')
        return redirect(url_for('spare_parts'))
    return render_template('spare_part_form.html', item={}, mode='new', purchase_sources=PURCHASE_SOURCE_LIST)

@app.route('/spare-parts/<int:part_id>/edit', methods=['GET','POST'])
@login_required
@role_required('Admin','Manager','Staff')
def spare_part_edit(part_id):
    con=db()
    item=row_to_dict(con.execute('SELECT * FROM spare_parts WHERE id=?',(part_id,)).fetchone())
    if not item:
        con.close(); flash('ไม่พบ Spare Part', 'danger'); return redirect(url_for('spare_parts'))
    if request.method=='POST':
        data=form_spare_part(item.get('image_link'))
        con.execute("""
            UPDATE spare_parts SET asset_code=?, product_id=?, sub_product_id=?, sn=?, image_link=?, name_product=?, part_type=?, equipment_name=?, warranty=?, purchase_id=?, purchase_source=?, supplier_name=?, po_number=?, country=?, warranty_expiry=?, qty=?, status=?, remark=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (data['asset_code'],data['product_id'],data['sub_product_id'],data['sn'],data['image_link'],data['name_product'],data['part_type'],data['equipment_name'],data['warranty'],data['purchase_id'],data['purchase_source'],data['supplier_name'],data['po_number'],data['country'],data['warranty_expiry'],data['qty'],data['status'],data['remark'],part_id))
        con.execute('INSERT INTO audit_log(action,field_name,old_value,new_value,actor) VALUES (?,?,?,?,?)',('SPARE_UPDATE','Spare Part',json.dumps(item,ensure_ascii=False),json.dumps(data,ensure_ascii=False),session.get('user')))
        con.commit(); con.close()
        flash('แก้ไข Spare Part สำเร็จ', 'success')
        return redirect(url_for('spare_parts'))
    con.close()
    return render_template('spare_part_form.html', item=item, mode='edit', purchase_sources=PURCHASE_SOURCE_LIST)

@app.route('/spare-parts/<int:part_id>/delete', methods=['POST'])
@login_required
@role_required('Admin','Manager')
def spare_part_delete(part_id):
    con=db()
    item=row_to_dict(con.execute('SELECT * FROM spare_parts WHERE id=?',(part_id,)).fetchone())
    con.execute('DELETE FROM spare_parts WHERE id=?',(part_id,))
    con.execute('INSERT INTO audit_log(action,field_name,old_value,actor) VALUES (?,?,?,?)',('SPARE_DELETE','Spare Part',json.dumps(item,ensure_ascii=False),session.get('user')))
    con.commit(); con.close()
    flash('ลบ Spare Part แล้ว', 'warning')
    return redirect(url_for('spare_parts'))


def generate_asset_code(product_id, sub_product_id):
    con=db()
    product=con.execute("SELECT product_name FROM product_assets WHERE product_id=?", (product_id,)).fetchone()
    code = product['product_name'] if product else (product_id or 'UNK')
    import re
    code = re.sub(r'[^A-Za-z0-9]+', '', str(code).upper())[:12] or 'UNK'
    sub = re.sub(r'[^A-Za-z0-9]+', '', str(sub_product_id or '0')).zfill(3)[-3:]
    prefix = f"{code}-{sub}-"
    row=con.execute("SELECT COUNT(*) AS c FROM spare_parts WHERE asset_code LIKE ?", (prefix+'%',)).fetchone()
    con.close()
    return f"{prefix}{(row['c'] or 0)+1:03d}"

def form_spare_part(existing_image=None):
    def val(name):
        return request.form.get(name) or None
    try:
        qty=int(request.form.get('qty') or 1)
    except Exception:
        qty=1

    uploaded_path = save_spare_image(request.files.get('image_file'))
    image_link = uploaded_path or val('image_link') or existing_image

    asset_code = val('asset_code')
    if not asset_code:
        asset_code = generate_asset_code(val('product_id'), val('sub_product_id'))

    return {
        'asset_code': asset_code,
        'product_id': val('product_id'),
        'sub_product_id': val('sub_product_id'),
        'sn': val('sn'),
        'image_link': image_link,
        'name_product': val('name_product'),
        'part_type': val('part_type'),
        'equipment_name': val('equipment_name'),
        'warranty': val('warranty'),
        'purchase_id': val('purchase_id'),
        'purchase_source': val('purchase_source') or 'Not Specified',
        'supplier_name': val('supplier_name'),
        'po_number': val('po_number'),
        'country': val('country'),
        'warranty_expiry': val('warranty_expiry'),
        'qty': qty,
        'status': val('status') or 'Active',
        'remark': val('remark')
    }

@app.route('/export/spare_parts.csv')
@login_required
def export_spare_parts_csv():
    import csv, io
    con=db()
    rows=con.execute('SELECT * FROM spare_parts ORDER BY equipment_name, part_type, name_product').fetchall()
    con.close()
    output=io.StringIO()
    if rows:
        writer=csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        for r in rows:
            writer.writerow(dict(r))
    csv_data='﻿' + output.getvalue()
    return Response(csv_data, mimetype='text/csv; charset=utf-8-sig', headers={'Content-Disposition':'attachment; filename=spare_parts_export.csv'})



@app.route('/product-structure')
@login_required
def product_structure():
    con=db()
    products=[dict(r) for r in con.execute("""
        SELECT pa.product_id, pa.product_name, COUNT(pc.id) AS component_count, COUNT(sp.id) AS spare_count
        FROM product_assets pa
        LEFT JOIN product_components pc ON pc.product_id = pa.product_id
        LEFT JOIN spare_parts sp ON sp.product_id = pa.product_id
        GROUP BY pa.product_id, pa.product_name
        ORDER BY CAST(pa.product_id AS INTEGER), pa.product_name
    """).fetchall()]
    selected=request.args.get('product_id') or (products[0]['product_id'] if products else None)
    components=[]
    if selected:
        components=[dict(r) for r in con.execute("""
            SELECT pc.*, COUNT(sp.id) AS spare_count, SUM(CASE WHEN sp.sn IS NOT NULL AND TRIM(sp.sn)<>'' THEN 1 ELSE 0 END) AS serial_count
            FROM product_components pc
            LEFT JOIN spare_parts sp ON sp.component_id = pc.id
            WHERE pc.product_id=?
            GROUP BY pc.id
            ORDER BY pc.sort_order, CAST(pc.sub_product_id AS INTEGER), pc.component_name
        """,(selected,)).fetchall()]
    con.close()
    return render_template('product_structure.html', products=products, selected=selected, components=components)


@app.route('/audit')
@login_required
@role_required('Admin','Manager')
def audit():
    con=db(); rows=[row_to_dict(r) for r in con.execute('SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 300').fetchall()]; con.close()
    return render_template('audit.html', rows=rows)

@app.route('/export/tasks.csv')
@login_required
def export_csv():
    import csv
    import io
    con=db()
    rows=con.execute('SELECT * FROM tasks').fetchall()
    con.close()
    output=io.StringIO()
    if rows:
        writer=csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        for r in rows:
            writer.writerow(dict(r))
    csv_data='﻿' + output.getvalue()
    return Response(
        csv_data,
        mimetype='text/csv; charset=utf-8-sig',
        headers={'Content-Disposition':'attachment; filename=task_export.csv'}
    )


@app.route('/export/knowledge_base.csv')
@login_required
def export_knowledge_base_csv():
    q=request.args.get('q','').strip()
    product=request.args.get('product','').strip()
    classification=request.args.get('classification','').strip()
    where=["(problem_summary IS NOT NULL OR root_cause IS NOT NULL OR solution_resolution IS NOT NULL)"]
    params=[]
    if q:
        where.append("""(task_description LIKE ? OR problem_summary LIKE ? OR root_cause LIKE ? OR troubleshooting_process LIKE ? OR solution_resolution LIKE ? OR preventive_action LIKE ? OR knowledge_tags LIKE ?)""")
        params += [f'%{q}%']*7
    if product:
        where.append("sub_product_id=?"); params.append(product)
    if classification:
        where.append("case_classification=?"); params.append(classification)
    sql='SELECT case_code, task_description, owner, status, priority, customer, sub_product_id, open_date, closed_date, case_classification, knowledge_tags, problem_summary, root_cause, troubleshooting_process, solution_resolution, preventive_action, evidence_link FROM tasks WHERE ' + ' AND '.join(where) + ' ORDER BY closed_date DESC, open_date DESC, id DESC'
    con=db()
    rows=con.execute(sql,params).fetchall()
    con.close()

    output=io.StringIO()
    fieldnames=['case_code','task_description','owner','status','priority','customer','sub_product_id','open_date','closed_date','case_classification','knowledge_tags','problem_summary','root_cause','troubleshooting_process','solution_resolution','preventive_action','evidence_link']
    writer=csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow({k: dict(r).get(k,'') for k in fieldnames})
    csv_data='﻿' + output.getvalue()
    return Response(csv_data, mimetype='text/csv; charset=utf-8-sig', headers={'Content-Disposition':'attachment; filename=knowledge_base_export.csv'})


@app.route('/export/knowledge_base.pdf')
@login_required
def export_knowledge_base_pdf():
    q=request.args.get('q','').strip()
    product=request.args.get('product','').strip()
    classification=request.args.get('classification','').strip()
    where=["(problem_summary IS NOT NULL OR root_cause IS NOT NULL OR solution_resolution IS NOT NULL)"]
    params=[]
    if q:
        where.append("""(task_description LIKE ? OR problem_summary LIKE ? OR root_cause LIKE ? OR troubleshooting_process LIKE ? OR solution_resolution LIKE ? OR preventive_action LIKE ? OR knowledge_tags LIKE ?)""")
        params += [f'%{q}%']*7
    if product:
        where.append("sub_product_id=?"); params.append(product)
    if classification:
        where.append("case_classification=?"); params.append(classification)
    sql='SELECT * FROM tasks WHERE ' + ' AND '.join(where) + ' ORDER BY closed_date DESC, open_date DESC, id DESC LIMIT 200'
    con=db()
    rows=[row_to_dict(r) for r in con.execute(sql,params).fetchall()]
    con.close()

    buffer=io.BytesIO()
    doc=SimpleDocTemplate(buffer, pagesize=A4, rightMargin=32, leftMargin=32, topMargin=32, bottomMargin=32)
    styles=getSampleStyleSheet()
    story=[]
    story.append(Paragraph('Task Tracker 2026 - Knowledge Base Report', styles['Title']))
    story.append(Paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', styles['Normal']))
    story.append(Paragraph(f'Total Knowledge Cases: {len(rows)}', styles['Normal']))
    story.append(Spacer(1, 12))

    if not rows:
        story.append(Paragraph('No knowledge base records found.', styles['Normal']))
    else:
        for item in rows:
            case_code = item.get('case_code') or f"TK-{(item.get('open_date') or datetime.now().strftime('%Y'))[:4]}-{item.get('id'):04d}"
            title = item.get('task_description') or '-'
            story.append(Paragraph(f'{case_code}: {title}', styles['Heading2']))
            meta = f"Product: {item.get('sub_product_id') or '-'} | Customer: {item.get('customer') or '-'} | Owner: {item.get('owner') or '-'} | Status: {item.get('status') or '-'}"
            story.append(Paragraph(meta, styles['Normal']))
            data=[
                ['Problem', item.get('problem_summary') or '-'],
                ['Root Cause', item.get('root_cause') or '-'],
                ['Troubleshooting', item.get('troubleshooting_process') or '-'],
                ['Solution', item.get('solution_resolution') or '-'],
                ['Preventive Action', item.get('preventive_action') or '-'],
            ]
            table=Table(data, colWidths=[110, 380])
            table.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(0,-1),colors.HexColor('#eef2ff')),
                ('TEXTCOLOR',(0,0),(0,-1),colors.HexColor('#111827')),
                ('GRID',(0,0),(-1,-1),0.25,colors.HexColor('#d1d5db')),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
                ('FONTSIZE',(0,0),(-1,-1),8),
                ('LEFTPADDING',(0,0),(-1,-1),6),
                ('RIGHTPADDING',(0,0),(-1,-1),6),
                ('TOPPADDING',(0,0),(-1,-1),6),
                ('BOTTOMPADDING',(0,0),(-1,-1),6),
            ]))
            story.append(table)
            story.append(Spacer(1, 14))

    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='knowledge_base_report.pdf', mimetype='application/pdf')

@app.route('/healthz')
def healthz():
    return jsonify({'status':'ok'})

@app.route('/api/summary')
@login_required
def api_summary():
    con=db(); rows=[row_to_dict(r) for r in con.execute('SELECT * FROM tasks').fetchall()]; con.close()
    return jsonify(calculate_metrics(rows))

ensure_production_database()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))