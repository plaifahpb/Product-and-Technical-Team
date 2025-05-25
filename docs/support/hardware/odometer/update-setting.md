#ขั้นตอนการอัปเดต ROMDAS Controller ผ่าน **โปรแกรม ROMDAS** <br><span style="color: #FF6600;">(UPDATING THE SETTINGS TO ROMDAS CONTROLLER)</span>

<span style="font-size: 25px;">
🛠️ขั้นตอนการอัปเดต ROMDAS Controller ผ่าน <strong>โปรแกรม ROMDAS</strong> 
</span>

- เมื่อมี**การตั้งค่าหรืออัปเดต Calibration Factor** ในโปรแกรม ROMDAS จำเป็น**ต้องอัปโหลดค่าการสอบเทียบใหม่นี้ไปยัง ROMDAS Controllerด้วย**
- เพื่อให้การทำงานของอุปกรณ์ฮาร์ดแวร์ เช่น Laser Profilers ทำงานได้อย่างถูกต้อง 
- ไปที่**เมนู Calibrate** | **Odometer** | **Update ROMDAS Controller Settings**

<img src="/assets/update.png" width="800" alt="set1">

- จะปรากฏหน้าต่างดังภาพด้านล่าง จากนั้น**คลิกที่ปุ่ม “Yes” เพื่อยืนยันการอัปเดตค่าการสอบเทียบไปยัง ROMDAS Controller**

<img src="/assets/update1.png" width="800" alt="set1">

---

- หน้าการตั้งค่า Update Interface Settings จะเปิดขึ้น

✅ **Minimum Speed**: ความเร็วขั้นต่ำที่ใช้ในการสำรวจ
<br>✅ **HRDMI Encoder Side**: เลือกฝั่งติดตั้ง HRDMI encoder (ซ้ายหรือขวาของรถ)
<br>✅ **Sampling Trigger Distance**: ระยะห่างในการเก็บข้อมูลของเลเซอร์แต่ละครั้ง ซึ่งส่งผลต่อความแม่นยำของการเก็บข้อมูลในระบบ ROMDAS

<img src="/assets/update2.png" width="800" alt="set1">

- เลือก **“Update ROMDAS Controller Settings”** เพื่อให้การตั้งค่าทั้งหมดที่กรอกไว้ในโปรแกรม ROMDAS ถูกส่งไปยังตัวควบคุม (interface)

⚠️ **สำคัญ**: **การตั้งค่า “Laser Safety Minimum Speed (km/h)”** มีผลเฉพาะเมื่อเชื่อมต่อกับโมดูล เช่น Laser Profiler, TPL หรือ LCMS เพื่อความปลอดภัย โดยกำหนดความเร็วขั้นต่ำที่ระบบเริ่มเก็บข้อมูลอัตโนมัติ

<img src="/assets/update3.png" width="800" alt="set1">

- สำหรับ**การตั้งค่า “Sampling Trigger Distance (mm)”**

✅ ใช้ค่า **1 mm** เมื่อต้องการเก็บ**ข้อมูล Texture และ Roughness**
<br>✅ ใช้ค่า **25 mm** เมื่อต้องการเก็บ**เฉพาะ Roughness**
<br>🟡 หมายเหตุ: **หากเก็บข้อมูลโดยใช้ค่า 25 mm จะ ไม่สามารถประมวลผลข้อมูล Texture ได้**

<img src="/assets/update4.png" width="800" alt="set1">

❗**หากมีความไม่ตรงกันระหว่างการตั้งค่าในซอฟต์แวร์ ROMDAS กับการตั้งค่าในอุปกรณ์ ROMDAS Controller (Interface)** ระบบจะแสดงข้อความแจ้งเตือนด้วย <span style="color:red">สีแดง (RED)</span> เพื่อให้ผู้ใช้ทราบและตรวจสอบก่อนดำเนินการต่อ