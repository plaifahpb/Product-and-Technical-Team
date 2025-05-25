# ขั้นตอนการปรับเทียบมาตรวัดระยะทาง <br><span style="color: #FF6600;">(ODOMETE CALIBRATION)</span>

<span style="font-size: 25px;">
การปรับเทียบค่าระยะทางโดยใช้ซอฟต์แวร์ <strong>ROMDAS</strong> ทำได้ตามขั้นตอนด้านล่างนี้
</span>

---

## 🛠️ ขั้นตอน:

1. เปิดซอฟต์แวร์ **ROMDAS**  
2. ไปที่เมนู `Calibration` > `Odometer`  
3. คลิก **"Run Odometer Calibration"**  
4. ปฏิบัติตามคำแนะนำที่แสดงในหน้าต่างโปรแกรม  


---

<img src="/assets/Run Odo calibration.png" width="850" alt="Run Odo calibration">

---

> 💡 **หมายเหตุ**  
ควรทำการสอบเทียบบนถนนที่ตรง มีระยะทางแน่นอน และไม่มีสิ่งกีดขวาง


---

## 🛠️ หน้าต่างแสดงการตั้งค่า Odometer Calibration

<img src="/assets/odometer-setup.png" width="850" alt="Odometer Calibration">


**คำอธิบายรายละเอียดแต่ละช่องในโปรแกรม:**

- **รหัสรถ (Vehicle ID):** ระบุชื่อหรือรหัสของรถที่ใช้ในการสอบเทียบ  
- **รหัสการสอบเทียบ ODO (Odo Calibration ID):**
<span style="white-space: nowrap;">
ระบบจะกำหนดอัตโนมัติโดยใช้ชื่อรถตามด้วยวันที่ เช่น <code>TestVehicle_201221</code> <span style="color: red;">(สามารถแก้ไขได้)
</span>


- **ความยาวช่วง (Section Length):** กรอกค่าความยาวถนนที่ใช้สอบเทียบ ไม่ควรต่ำกว่า 300 เมตร  
- **ความดันลมยาง (Tyre Pressure):** ระบุค่าความดันลมยางของรถ  
- **เลขไมล์ปัจจุบันของรถ (Vehicle ODO):** กรอกเลขไมล์ของรถในปัจจุบัน  
- **ค่าปัจจัยที่ใช้อยู่ (Current Factor):** ค่าการสอบเทียบก่อนหน้า (ถ้ามี)

---

### ⚙️ ขั้นตอนที่ 1

- กรอกรายละเอียดในหัวข้อ **“Calibration Odometer Settings”**  
  และคลิก <span>**“เริ่มการสอบเทียบ (Start Calibration)”**</span>  
  จากนั้น <span style="color: green;">เครื่องหมายสีเขียวจะเลื่อนไปจาก**ขั้นตอนที่ 1** ไปยัง**ขั้นตอนที่ 2**</span>

<img src="/assets/odometer-step1.png" alt="Step 1: Calibration Odometer Settings" width="850">


---

### ⚙️ ขั้นตอนที่ 2 <a id="step-2"></a>

- นำรถไปจอดที่จุดเริ่มต้นของช่วงที่ใช้สอบเทียบ แล้ว **กดปุ่ม [SPACE]** บนแป้นพิมพ์  
  <span style="color: red;">หมายเหตุ : รถควรจอดอยู่ที่จุดเริ่มต้นของช่วงสอบเทียบ</span>
  
**📍 Site Odometer Calibration ที่แนะนำ**:  [Google Maps – คลิกเพื่อเปิดแผนที่](https://maps.app.goo.gl/aFFsMMUj57n8EevSA?g_st=a)

<img src="/assets/odometer-step2-bottom.png" alt="Step 2 Bottom" width="850">

<img src="/assets/odometer-step2-top.png" alt="Step 2 Top" width="850">


### ⚙️ ขั้นตอนที่ 3

- **เมื่อกดปุ่ม [SPACE]** ระบบจะเริ่มรับสัญญาณพัลส์จากตัวควบคุม **ROMDAS**
- เมื่อรถถึงจุดสิ้นสุดของช่วงสอบเทียบ **ให้กด [SPACE]** อีกครั้งเพื่อหยุดการบันทึกข้อมูล
- ✅ เครื่องหมายสีเขียวจะเลื่อนไปจาก**ขั้นตอนที่ 3** ไปยัง**ขั้นตอนที่ 4**

<img src="/assets/step3-setup.png" alt="สิ้นสุดการสอบเทียบ" width="850">

<img src="/assets/step3-driving.png" alt="รถวิ่งสอบเทียบ 300 เมตร" width="850">

---

### ⚙️ ขั้นตอนที่ 4

- กดปุ่ม “**Calculate**” เพื่อคำนวณค่าปัจจัยการสอบเทียบ (**Calibration Factor**)  
- ซึ่งระบบจะเพิ่มผลลัพธ์ที่ได้ลงในหน้าต่างผลการรัน (**Run Result**)

<img src="/assets/step4-calculate.png" alt="Step 4 Calculate" width="850">

---

### ⚙️ ขั้นตอนที่ 5

- หลังจากการสอบเทียบครั้งแรกเสร็จ ให้คลิก **“Do another Run”**
- เครื่องหมายสีเขียวจะเลื่อนไปยังขั้นตอนที่ 2 จากนั้นให้รถกลับไปจุดเริ่มต้นของช่วงสอบเทียบ และทำซ้ำขั้นตอนเดิมอย่างน้อย **3 ครั้ง**

<img src="/assets/run-5.png" alt="run-5" width="850">

**หมายเหตุ**: ต้องทำการสอบเทียบ**อย่างน้อย 3 ครั้ง** (3 runs) เพื่อให้ผ่านระดับความเชื่อมั่น (Confidence Level) สำหรับการสอบเทียบ ODO

### ⚙️ ขั้นตอนที่ 5-1

- การตรวจสอบความถูกต้องของค่าการสอบเทียบ **(Calibration Factor Validation)**  
  หากระดับความเชื่อมั่นของ **ค่าการสอบเทียบแสดงว่า "ผ่าน (PASS)"** ผู้ใช้งานสามารถเลือกที่จะทำการสอบเทียบเพิ่มเติมโดย  
  **คลิก "Do Another Run"** หรือคลิก **"Validate Calibration" เพื่อยืนยันค่าการสอบเทียบ**

<img src="/assets/step-5-1.png" alt="step-5-1" width="850"> 
  
- **การยืนยันค่าการสอบเทียบ (Validate Calibration)** จะทำได้เฉพาะเมื่อระดับความเชื่อมั่นของค่าที่สอบเทียบเป็น **“PASS” เท่านั้น**
- ในการยืนยันค่าการสอบเทียบ **ให้คลิก “Validate Calibration”** แล้วนำรถไปจอดที่จุดเริ่มต้นของช่วงสอบเทียบ [ตามขั้นตอนที่ 2](#step-2)
 และ**กดปุ่ม [SPACE]**
- ข้อมูลใน Status Log จะถูกอัปเดต โดยค่าระยะทาง (Chainage) จะแสดงการเพิ่มขึ้นตามลำดับ
- **เมื่อรถถึงจุดสิ้นสุดของช่วงสอบเทียบ** (300 เมตร) ให้**กดปุ่ม [SPACE]** อีกครั้ง**เพื่อหยุดการบันทึกข้อมูล**

<img src="/assets/step-5-2.png" alt="step-5-1" width="850">

### ⚙️ ขั้นตอนที่ 6

- **หากการทดสอบยืนยัน (Validation Run) ผ่าน** ระบบจะแสดงข้อความใน Status Log ว่า **“Validation Passed”** <br> 
- จากนั้นจะมีปุ่มใหม่ปรากฏขึ้น คือ **“Save Calibration”** ให้**ติ๊กเลือก “Set as default”** และ**คลิก “Save Calibration”**

<img src="/assets/step-6.png" alt="step-6" width="850">

- ระบบจะแสดง log **เพื่อยืนยันว่าค่าการสอบเทียบ ODO ได้ถูกอัปเดตเข้าสู่ ROMDAS controller แล้ว** <br>จากนั้นสามารถออกจากกระบวนการสอบเทียบได้ 

<img src="/assets/step-6-1.png" alt="step-6" width="850">

### ⚙️ ขั้นตอนที่ 7

- เมื่อคลิกปุ่ม **“Save Calibration”** ค่าปัจจัยการสอบเทียบจะถูกอัปเดตเข้าสู่ ROMDAS controller โดยอัตโนมัติ  
- ✅ **ผลการสอบเทียบจะถูกบันทึกลงในไฟล์ Excel** โดยใช้ชื่อไฟล์ว่า  
  **`Odo Calib_Odo Calibration ID_Date (YYMMDD)`**
- ซึ่งชื่อ Odo Calibration ID จะเป็นค่าที่กำหนดไว้ตั้งแต่เริ่มต้นกระบวนการสอบเทียบ ODO  

<img src="/assets/step-7.png" alt="left" width="650">
<img src="/assets/step-7-1.png" alt="right" width="650">










