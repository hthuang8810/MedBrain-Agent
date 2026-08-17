-- 创建数据库和表结构
CREATE DATABASE IF NOT EXISTS medical_system;
USE medical_system;

-- 创建科室表
CREATE TABLE departments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    floor INT,
    head_doctor VARCHAR(50),
    established_date DATE
);

-- 创建医生表
CREATE TABLE doctors (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    department_id INT,
    specialty VARCHAR(100),
    license_number VARCHAR(20),
    phone VARCHAR(20),
    email VARCHAR(100),
    hire_date DATE,
    salary DECIMAL(10,2),
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- 创建病人表
CREATE TABLE patients (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    id_card VARCHAR(18),
    gender ENUM('男','女'),
    birth_date DATE,
    phone VARCHAR(20),
    emergency_contact VARCHAR(50),
    blood_type ENUM('A','B','AB','O'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建病历表
CREATE TABLE medical_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    doctor_id INT,
    department_id INT,
    chief_complaint TEXT,
    diagnosis TEXT,
    treatment_plan TEXT,
    visit_date DATE,
    next_visit_date DATE,
    fee DECIMAL(8,2),
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id),
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- 创建药品表
CREATE TABLE medicines (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    manufacturer VARCHAR(100),
    unit_price DECIMAL(8,2),
    stock_quantity INT,
    prescription_required BOOLEAN,
    approval_number VARCHAR(50)
);

-- 创建处方表
CREATE TABLE prescriptions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    record_id INT,
    medicine_id INT,
    dosage VARCHAR(50),
    frequency VARCHAR(50),
    duration_days INT,
    quantity INT,
    FOREIGN KEY (record_id) REFERENCES medical_records(id),
    FOREIGN KEY (medicine_id) REFERENCES medicines(id)
);

-- 插入科室数据
INSERT INTO departments (name, floor, head_doctor, established_date) VALUES
('急诊科', 1, '陈志强', '2010-05-15'),
('心内科', 3, '王海峰', '2008-08-20'),
('神经内科', 4, '李建军', '2012-03-10'),
('呼吸科', 3, '张雪梅', '2009-11-25'),
('消化内科', 2, '刘建国', '2011-07-30'),
('骨科', 5, '赵大伟', '2007-09-12'),
('妇产科', 6, '孙丽华', '2010-01-18'),
('儿科', 7, '周小燕', '2013-06-08');

-- 插入医生数据
INSERT INTO doctors (name, department_id, specialty, license_number, phone, email, hire_date, salary) VALUES
('陈志强', 1, '急诊医学', 'DL201005151', '13800138001', 'chenzq@hospital.com', '2010-06-01', 25000.00),
('王海峰', 2, '心血管疾病', 'DL200808201', '13800138002', 'wanghf@hospital.com', '2008-09-01', 28000.00),
('李建军', 3, '神经系统疾病', 'DL201203101', '13800138003', 'lijj@hospital.com', '2012-04-01', 26000.00),
('张雪梅', 4, '呼吸系统疾病', 'DL200911251', '13800138004', 'zhangxm@hospital.com', '2010-01-01', 24000.00),
('刘建国', 5, '消化系统疾病', 'DL201107301', '13800138005', 'liujg@hospital.com', '2011-08-01', 25500.00),
('赵大伟', 6, '创伤骨科', 'DL200709121', '13800138006', 'zhaodw@hospital.com', '2007-10-01', 27000.00),
('孙丽华', 7, '妇产科学', 'DL201001181', '13800138007', 'sunlh@hospital.com', '2010-02-01', 26500.00),
('周小燕', 8, '儿科学', 'DL201306081', '13800138008', 'zhouxy@hospital.com', '2013-07-01', 23000.00),
('吴天明', 2, '心脏介入', 'DL201508152', '13800138009', 'wutm@hospital.com', '2015-09-01', 22000.00),
('郑美丽', 7, '妇科肿瘤', 'DL201612202', '13800138010', 'zhengml@hospital.com', '2017-01-01', 21000.00);

-- 插入病人数据
INSERT INTO patients (name, id_card, gender, birth_date, phone, emergency_contact, blood_type) VALUES
('王小虎', '110101198510123456', '男', '1985-10-12', '13900139001', '李小红', 'A'),
('张丽华', '110101198803204567', '女', '1988-03-20', '13900139002', '王大明', 'B'),
('李明轩', '110101199205157890', '男', '1992-05-15', '13900139003', '李建国', 'O'),
('刘思思', '110101199508081234', '女', '1995-08-08', '13900139004', '刘志强', 'AB'),
('陈大勇', '110101197812253456', '男', '1978-12-25', '13900139005', '陈小芳', 'A'),
('赵婷婷', '110101198611117890', '女', '1986-11-11', '13900139006', '赵大刚', 'B'),
('孙志强', '110101199009091234', '男', '1990-09-09', '13900139007', '孙美丽', 'O'),
('周小敏', '110101199312125678', '女', '1993-12-12', '13900139008', '周大伟', 'A');

-- 插入病历数据
INSERT INTO medical_records (patient_id, doctor_id, department_id, chief_complaint, diagnosis, treatment_plan, visit_date, next_visit_date, fee) VALUES
(1, 2, 2, '胸闷、心悸3天', '冠心病', '药物治疗，定期复查', '2024-01-15', '2024-02-15', 350.00),
(2, 4, 4, '咳嗽、发热2周', '支气管炎', '抗生素治疗，休息', '2024-01-16', NULL, 280.50),
(3, 3, 3, '头痛、头晕1个月', '偏头痛', '对症治疗，生活调整', '2024-01-17', '2024-02-17', 420.00),
(4, 5, 5, '胃痛、反酸2周', '胃炎', '药物治疗，饮食调整', '2024-01-18', '2024-02-18', 310.00),
(5, 6, 6, '膝关节疼痛3个月', '骨关节炎', '物理治疗，药物治疗', '2024-01-19', '2024-03-19', 580.00),
(6, 7, 7, '月经不调半年', '内分泌失调', '激素治疗，定期检查', '2024-01-20', '2024-02-20', 460.00),
(7, 1, 1, '高热、呕吐1天', '急性肠胃炎', '补液，对症治疗', '2024-01-21', NULL, 390.00),
(8, 8, 8, '儿童发热、咳嗽3天', '上呼吸道感染', '抗感染治疗', '2024-01-22', NULL, 270.00);

-- 插入药品数据
INSERT INTO medicines (name, type, manufacturer, unit_price, stock_quantity, prescription_required, approval_number) VALUES
('阿莫西林胶囊', '抗生素', '华北制药', 25.80, 500, TRUE, '国药准字H130201'),
('布洛芬缓释胶囊', '解热镇痛', '中美天津史克', 18.50, 300, FALSE, '国药准字H109000'),
('阿托伐他汀钙片', '降血脂', '辉瑞制药', 45.60, 200, TRUE, '国药准字J201200'),
('胰岛素注射液', '降血糖', '诺和诺德', 68.00, 150, TRUE, '国药准字S201300'),
('奥美拉唑肠溶胶囊', '胃药', '阿斯利康', 32.40, 400, TRUE, '国药准字H200464'),
('氨氯地平片', '降压药', '辉瑞制药', 28.90, 350, TRUE, '国药准字H109502'),
('头孢克肟片', '抗生素', '广州白云山', 38.20, 280, TRUE, '国药准字H200305'),
('维生素C片', '维生素', '石药集团', 8.50, 1000, FALSE, '国药准字H130212');

-- 插入处方数据
INSERT INTO prescriptions (record_id, medicine_id, dosage, frequency, duration_days, quantity) VALUES
(1, 3, '10mg', '每日一次', 30, 30),
(1, 6, '5mg', '每日一次', 30, 30),
(2, 1, '0.5g', '每日三次', 7, 21),
(2, 2, '0.3g', '每日两次', 5, 10),
(3, 2, '0.3g', '必要时', 30, 10),
(4, 5, '20mg', '每日一次', 14, 14),
(5, 2, '0.3g', '每日三次', 10, 30),
(6, 7, '0.1g', '每日两次', 7, 14),
(7, 1, '0.5g', '每日三次', 5, 15),
(8, 8, '0.1g', '每日一次', 10, 10);

-- 创建检查项目表
CREATE TABLE medical_exams (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    normal_range TEXT,
    price DECIMAL(8,2),
    duration_minutes INT
);

-- 插入检查项目数据
INSERT INTO medical_exams (name, category, normal_range, price, duration_minutes) VALUES
('血常规', '血液检查', '白细胞:4-10×10^9/L', 80.00, 30),
('心电图', '心脏检查', '正常窦性心律', 120.00, 20),
('胸部CT', '影像检查', '双肺纹理清晰', 450.00, 60),
('腹部B超', '超声检查', '肝胆胰脾未见异常', 200.00, 30),
('肝功能', '生化检查', 'ALT:0-40U/L', 150.00, 120),
('肾功能', '生化检查', '肌酐:44-133umol/L', 120.00, 120);

-- 创建检查记录表
CREATE TABLE exam_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    record_id INT,
    exam_id INT,
    exam_date DATE,
    result TEXT,
    FOREIGN KEY (record_id) REFERENCES medical_records(id),
    FOREIGN KEY (exam_id) REFERENCES medical_exams(id)
);

-- 插入检查记录数据
INSERT INTO exam_records (record_id, exam_id, exam_date, result) VALUES
(1, 2, '2024-01-15', 'ST段轻度压低'),
(1, 1, '2024-01-15', '白细胞:8.5×10^9/L'),
(2, 1, '2024-01-16', '白细胞:12.8×10^9/L'),
(3, 4, '2024-01-17', '肝胆胰脾未见异常'),
(4, 5, '2024-01-18', 'ALT:35U/L');