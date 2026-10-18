/* ==========================================================================
   Clearbrook 糖尿病中心（CDC）集中数据库
   建表脚本 —— 与 ERD / 类图严格对应
   目标：SQL Server 2019+（CHAR / VARCHAR / DECIMAL 语义亦可直接迁移至 MySQL 8）
   约定：
     1) 每张表设独立代理主键，领域组合字段另加唯一约束；
     2) 外键显式命名，便于回溯到 ERD 中的关系线；
     3) 软删除与审计字段不在本作业范围内，故未列出。
   ========================================================================== */

/* ---------- 01 中心与诊室 ------------------------------------------------ */

CREATE TABLE Center (
    CenterID      CHAR(4)      NOT NULL,
    CenterName    VARCHAR(50)  NOT NULL,
    Address       VARCHAR(100) NOT NULL,
    Phone         VARCHAR(20)  NOT NULL,
    Email         VARCHAR(50)  NOT NULL,
    DirectorName  VARCHAR(50)  NOT NULL,
    CONSTRAINT PK_Center PRIMARY KEY (CenterID)
);

CREATE TABLE Room (
    CenterID   CHAR(4) NOT NULL,
    RoomNo     CHAR(4) NOT NULL,
    SeatCount  INT     NOT NULL,
    CONSTRAINT PK_Room PRIMARY KEY (CenterID, RoomNo),          -- 组合主键
    CONSTRAINT FK_Room_Center FOREIGN KEY (CenterID)
        REFERENCES Center (CenterID)
);

CREATE TABLE Resource (
    ResourceID    CHAR(10)     NOT NULL,
    ResourceName  VARCHAR(50)  NOT NULL,
    PurchaseDate  DATE         NULL,
    Remark        VARCHAR(100) NULL,
    CenterID      CHAR(4)      NOT NULL,
    RoomNo        CHAR(4)      NOT NULL,
    CONSTRAINT PK_Resource PRIMARY KEY (ResourceID),
    CONSTRAINT FK_Resource_Room FOREIGN KEY (CenterID, RoomNo)
        REFERENCES Room (CenterID, RoomNo)                      -- 组合：不允许为空
);

/* ---------- 02 临床人员 -------------------------------------------------- */

CREATE TABLE CDE (
    CDEID        CHAR(8)     NOT NULL,
    Name         VARCHAR(50) NOT NULL,
    StaffNo      CHAR(9)     NOT NULL,
    HireDate     DATE        NOT NULL,
    WorkPhone    VARCHAR(20) NOT NULL,
    HomePhone    VARCHAR(20) NOT NULL,
    WorkEmail    VARCHAR(50) NOT NULL,
    MobilePhone  VARCHAR(20) NULL,
    CONSTRAINT PK_CDE PRIMARY KEY (CDEID),
    CONSTRAINT UQ_CDE_StaffNo UNIQUE (StaffNo)                  -- 9 位员工编号
);

CREATE TABLE Qualification (
    QualID    CHAR(4)     NOT NULL,
    QualName  VARCHAR(30) NOT NULL,
    CONSTRAINT PK_Qualification PRIMARY KEY (QualID)
);

CREATE TABLE CDE_Qualification (                                -- 多对多关联表
    CDEID   CHAR(8) NOT NULL,
    QualID  CHAR(4) NOT NULL,
    CONSTRAINT PK_CDE_Qualification PRIMARY KEY (CDEID, QualID),
    CONSTRAINT FK_CQ_CDE  FOREIGN KEY (CDEID)  REFERENCES CDE (CDEID),
    CONSTRAINT FK_CQ_Qual FOREIGN KEY (QualID) REFERENCES Qualification (QualID)
);

/* ---------- 03 患者与并发症 ---------------------------------------------- */

CREATE TABLE Patient (
    PatientID       CHAR(8)      NOT NULL,
    FullName        VARCHAR(50)  NOT NULL,
    MailingAddress  VARCHAR(100) NOT NULL,
    Phone           VARCHAR(20)  NOT NULL,
    Email           VARCHAR(50)  NULL,                          -- 仅邮箱可为空
    BirthDate       DATE         NOT NULL,
    DiagnosisDate   DATE         NOT NULL,
    DiabetesType    VARCHAR(10)  NOT NULL,                      -- 1型/2型/妊娠期/前期
    CONSTRAINT PK_Patient PRIMARY KEY (PatientID)
);

CREATE TABLE Complication (
    CompID    CHAR(4)     NOT NULL,
    CompName  VARCHAR(50) NOT NULL,
    CONSTRAINT PK_Complication PRIMARY KEY (CompID)
);

CREATE TABLE Patient_Complication (                             -- 多对多关联表
    PatientID  CHAR(8)      NOT NULL,
    CompID     CHAR(4)      NOT NULL,
    OnsetDate  DATE         NULL,
    Remark     VARCHAR(100) NULL,
    CONSTRAINT PK_Patient_Complication PRIMARY KEY (PatientID, CompID),
    CONSTRAINT FK_PC_Patient FOREIGN KEY (PatientID) REFERENCES Patient (PatientID),
    CONSTRAINT FK_PC_Comp    FOREIGN KEY (CompID)    REFERENCES Complication (CompID)
);

/* ---------- 04 预约 ------------------------------------------------------ */

CREATE TABLE Appointment (
    ApptID        CHAR(10)     NOT NULL,
    PatientID    CHAR(8)      NOT NULL,
    CDEID        CHAR(8)      NOT NULL,
    CenterID     CHAR(4)      NOT NULL,
    RoomNo       CHAR(4)      NOT NULL,
    ApptDate     DATE         NOT NULL,
    ApptTime     TIME         NOT NULL,
    Status       VARCHAR(6)   NOT NULL,                         -- 到诊/改期/取消
    ClinicalNote VARCHAR(200) NULL,
    CONSTRAINT PK_Appointment PRIMARY KEY (ApptID),
    CONSTRAINT FK_Appt_Patient FOREIGN KEY (PatientID) REFERENCES Patient (PatientID),
    CONSTRAINT FK_Appt_CDE     FOREIGN KEY (CDEID)     REFERENCES CDE (CDEID),
    CONSTRAINT FK_Appt_Room    FOREIGN KEY (CenterID, RoomNo)
        REFERENCES Room (CenterID, RoomNo),
    CONSTRAINT CK_Appt_Status CHECK (Status IN ('到诊', '改期', '取消'))
);

/* ---------- 05 血糖与胰岛素 ---------------------------------------------- */

CREATE TABLE BloodGlucose (
    ReadingID     CHAR(12)     NOT NULL,
    PatientID     CHAR(8)      NOT NULL,
    TestDateTime  DATETIME     NOT NULL,
    GlucoseValue  DECIMAL(4,1) NOT NULL,
    Remark        VARCHAR(100) NULL,
    CONSTRAINT PK_BloodGlucose PRIMARY KEY (ReadingID),
    CONSTRAINT UQ_BG_Patient_Time UNIQUE (PatientID, TestDateTime),  -- 业务唯一键
    CONSTRAINT FK_BG_Patient FOREIGN KEY (PatientID) REFERENCES Patient (PatientID)
);

CREATE TABLE Injection (
    InjectionID  CHAR(12)    NOT NULL,
    ReadingID    CHAR(12)    NOT NULL,
    InjType      VARCHAR(6)  NOT NULL,                          -- 餐时/基础
    Units        INT         NOT NULL,
    InjTime      DATETIME    NOT NULL,
    CONSTRAINT PK_Injection PRIMARY KEY (InjectionID),
    CONSTRAINT UQ_Injection_Reading UNIQUE (ReadingID),         -- 1 : 0..1
    CONSTRAINT FK_Injection_BG FOREIGN KEY (ReadingID) REFERENCES BloodGlucose (ReadingID)
);

/* ---------- 06 营养记录 -------------------------------------------------- */

CREATE TABLE Nutrition (
    NutriID       CHAR(12)     NOT NULL,
    PatientID     CHAR(8)      NOT NULL,
    NutriDate     DATE         NOT NULL,
    MealCount     INT          NOT NULL,
    TotalCalorie  INT          NOT NULL,
    FatRatio      DECIMAL(3,1) NOT NULL,
    ProteinRatio  DECIMAL(3,1) NOT NULL,
    CarbRatio     DECIMAL(3,1) NOT NULL,
    CONSTRAINT PK_Nutrition PRIMARY KEY (NutriID),
    CONSTRAINT UQ_Nutrition_Patient_Date UNIQUE (PatientID, NutriDate),
    CONSTRAINT FK_Nutrition_Patient FOREIGN KEY (PatientID) REFERENCES Patient (PatientID)
);

/* ==========================================================================
   关键业务规则（与用例规约 / 设计报告一致）
   --------------------------------------------------------------------------
   R1  血糖读数由 (PatientID, TestDateTime) 唯一标识        → UQ_BG_Patient_Time
   R2  异常血糖值必须填写备注                                → 应用层校验
   R3  一份营养记录唯一对应一位患者的一个日期                 → UQ_Nutrition_Patient_Date
   R4  一次注射只对应一次读数，读数可无注射                   → UQ_Injection_Reading
   R5  诊室由 (CenterID, RoomNo) 双重标识                    → PK_Room
   R6  预约状态仅有到诊/改期/取消                             → CK_Appt_Status
   ========================================================================== */
