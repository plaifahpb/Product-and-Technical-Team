# Task Tracker Internal 2026 — Production Web Dashboard

ระบบนี้สร้างจากไฟล์ `TASK TRACKER INTERNAL_2026.xlsx` และแปลงข้อมูลหลักจาก Sheet `Task` เป็น SQLite Database เพื่อให้ใช้งานแบบ Web Dashboard ได้ทันที

## Features
- Login / Role: Admin, Manager, Staff, Viewer
- Executive Dashboard: KPI, Status, Owner, Priority, Upcoming Tasks
- Task Management: เพิ่ม/แก้ไข/ลบ/ค้นหา/Filter
- Calendar View: แสดงงานตาม Due Date
- Analytics: Monthly Trend และ Owner x Status
- Audit Log: บันทึกการเพิ่ม/แก้ไข/ลบข้อมูล
- Export CSV

## Demo Login
- Admin: `admin` / `admin123`
- Manager: `manager` / `manager123`
- Staff: `staff` / `staff123`
- Viewer: `viewer` / `viewer123`

## วิธีติดตั้ง
```bash
cd task_tracker_web_dashboard
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
python app.py
```

เปิด Browser:
```text
http://127.0.0.1:5000
```

## Deploy Production แนะนำ
สำหรับใช้งานในทีมจริง แนะนำ:
- Server: Ubuntu / Windows Server
- Web Server: Nginx หรือ IIS Reverse Proxy
- WSGI: Gunicorn / Waitress
- Database: PostgreSQL แทน SQLite ถ้ามีผู้ใช้พร้อมกันจำนวนมาก
- Auth: Google Workspace Login หรือ Microsoft Entra ID

## โครงสร้างข้อมูลหลัก
ตาราง `tasks` อ้างอิงจาก Header แถว 27 ของ Sheet `Task`:
- task_description
- category
- owner
- priority
- status
- due_date
- important
- urgent
- note
- day_remaining_auto
- sub_product_id
- customer
- open_date
- closed_date
- kpi_result
- ms_team

## หมายเหตุ
ระบบนี้เป็น Production-ready prototype ที่พร้อมนำไปต่อยอดจริง โดยยังใช้ SQLite เพื่อให้เปิดใช้งานง่ายที่สุดก่อน หากจะใช้งานหลายคนพร้อมกันในองค์กรควรย้าย Database เป็น PostgreSQL

## Update: Product Master
- Admin/Manager สามารถเพิ่ม Product/Device ใหม่ได้ที่เมนู Product Master
- Product ใหม่จะถูกใช้ใน Add/Edit Task และ Product Filter ทันที
- เหมาะสำหรับรองรับอุปกรณ์ใหม่ที่เข้ามาในอนาคต


## Spare Parts
Open menu **Spare Parts** or go directly to `http://127.0.0.1:5000/spare-parts`.

## Spare Part Images
In the Spare Parts page, click the Part / Spare Name to open an image preview modal.

To show real equipment images:
1. Put image files in `static/spare_parts/`
2. Edit the spare part
3. Fill `Image Link / Description` with `/static/spare_parts/<filename>.jpg`

External image URLs also work if they start with `http://` or `https://`.

## Spare Part Image Upload
The Spare Parts module now supports image upload directly from the dashboard.

How to use:
1. Open `Spare Parts`
2. Click `Add Spare Part` or `Edit`
3. Choose an image in `Upload Image`
4. Save

Uploaded images are stored automatically in:
`static/spare_parts/`

The saved image path is written to the spare part record and can be previewed by clicking the Part / Spare Name.

## Product Structure Update
This version restructures Spare Parts into:
- Product Master: Product ID → Product Name
- Product Components: Product ID + Sub Product ID → Component/Spare name
- Spare Parts: linked to Product and Component

Initial mapping from user requirement:
1 = LCMS
2 = TPL1
3 = TPL2
4 = RS10
5 = AU20
6 = i73+ GNSS
7 = CHC - iBASE
8 = Xenomatix

Imported from TP - Database202_sub1.xlsx:
- Products: 10
- Components: 369
- Spare Parts: 371

## Final Asset & Spare Part Structure
Final fields added:
- Asset Code: human-readable inventory code, auto-generated if blank
- Purchase Source: OEM Direct / Local Supplier / Distributor / Internal Fabrication / RMA Replacement / Not Specified
- Supplier Name
- PO / Invoice No.
- Country
- Warranty Expiry

Recommended code format:
`PRODUCT-SUBPRODUCT-RUNNING`
Example:
`LCMS-012-001`, `AU20-003-001`

## Case Knowledge Base
Final Task module includes case knowledge fields:
- Problem Summary
- Root Cause
- Troubleshooting Process
- Solution / Resolution
- Preventive Action
- Repeated Issue flag
- Knowledge Tags
- Evidence Link
- Spare Parts Used linked to the Spare Parts module

Use `Knowledge Base` menu to search previous cases and solutions.

## Production Final Notes
This final version includes:
- Human-readable Case ID: TK-YYYY-0001
- Clickable Task Case Detail
- Case Knowledge Base: Problem, Root Cause, Troubleshooting, Solution, Preventive Action
- Repeated / Known Issue flag
- Evidence Link
- Spare Parts Used linked to each case
- Product Structure: Product ID → Sub Product ID
- Asset Code for spare parts
- Purchase Source / Supplier / PO / Warranty tracking
- Image Upload and Preview for Spare Parts

Recommended team workflow:
1. Create Task
2. Update Status and KPI fields
3. Open Case Detail
4. Fill Case Knowledge after resolution
5. Link any Spare Parts Used
6. Search Knowledge Base when similar issues occur again


## Enterprise Production Package
Run production server:
`python production_server.py`

Windows:
Double-click `run_production_server.bat`

Accounts:
- Admin: SBDTP / SBDTP
- Internal Team: SBD_Internal / SBD_Internal
- Viewer: iNFRA / iNFRA

This package includes:
- Waitress production WSGI server
- Dockerfile
- Render config
- Health check `/healthz`
- Hashed passwords
- Backup script
- Upload folders for spare part and case images
