-- 可选：仅在需要时执行
-- CREATE DATABASE ailawyer;

--客户表
CREATE TABLE IF NOT EXISTS clients (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  type VARCHAR(50) DEFAULT '个人',
  phone VARCHAR(50),
  address VARCHAR(50),--地址
  cases INT DEFAULT 0,--案件数量
  sstatus INT DEFAULT 0,--状态 0 联系中 1已签单
  status_name VARCHAR(50) DEFAULT '未受理',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--案件表
CREATE TABLE IF NOT EXISTS cases (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL,--案件名称
  plaintiff VARCHAR(200),--原告
  defendant VARCHAR(200),--被告
  location VARCHAR(200),--法院地址
  status INT DEFAULT 0,--状态 0未受理 1已受理，3.已结案
  status_name VARCHAR(50) DEFAULT '未受理',
  claims VARCHAR(2000),--诉讼请求
  facts VARCHAR(4000),--事实与理由
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--文件表
CREATE TABLE IF NOT EXISTS files (
  id SERIAL PRIMARY KEY,
  p_id INT ,--关联ID
  name VARCHAR(200) NOT NULL,--文件名称
  doc_url VARCHAR(200) NOT NULL,--文件路径
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--合同表
CREATE TABLE IF NOT EXISTS contracts (
  id SERIAL PRIMARY KEY,
  contract_name VARCHAR(200) ,--合同名称
  type VARCHAR(100),--合同类型
  hasRisk boolean DEFAULT false ,--是否有风险
  high_risk INT DEFAULT 0,--高风险 
  medium_risk INT DEFAULT 0,--中风险 
  low_risk INT DEFAULT 0,--低风险
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--合同审查表
CREATE TABLE IF NOT EXISTS contract_review (
  id SERIAL PRIMARY KEY,
  contract_id INT NOT null,--合同ID
  title VARCHAR(100) ,--原文章节+标题 ：第八条 违约责任/第十二条 交付条件
  risk_level VARCHAR(50) ,--风险等级high-高风险、medium-中风险、low-低风险
  position VARCHAR(20),--审查立场:中立，甲方，乙方
  method VARCHAR(1000),--分析方法  
  risk_clause VARCHAR(1000),--风险描述  担保效力审查相关的风险/合同的格式审查/违约责任/交付条件
  result_type VARCHAR(300), --需修改/新增/保持原文
  original_content VARCHAR(1000),--合同原文
  suggestion VARCHAR(1000),--修改建议	
  result_content VARCHAR(1000),--修改后文本	
  legal_basis VARCHAR(1000),--法律依据
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


--文书表
CREATE TABLE IF NOT EXISTS documents (
  id SERIAL PRIMARY KEY,
  case_id INT NOT NULL,
  case_name VARCHAR(200),--关联的案件
  doc_name VARCHAR(200) ,--文书名称
  doc_type VARCHAR(100),--文书类型
  doc_content VARCHAR(300),--文件内容
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--爬虫客户
CREATE TABLE IF NOT EXISTS spider_customers (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL,--客户名称
  job VARCHAR(200),--职业
  city VARCHAR(100),--城市
  co_size VARCHAR(100),--规模
  phone VARCHAR(500),--联系电话
  status INT DEFAULT 0,--状态 0未联系 1已联系，3.无法联系
  status_name VARCHAR(50) DEFAULT '未联系',
  remark text ,--客户简介
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--律所表
CREATE TABLE IF NOT EXISTS firms (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  contact VARCHAR(200),--联系人
  phone VARCHAR(50),--电话
  address VARCHAR(300),--地址
  city VARCHAR(100),--城市
  status INT DEFAULT 0,--状态 0未启用 1启用，3.套餐余额不足
  status_name VARCHAR(50) DEFAULT '未启用',
  employees INT DEFAULT 0,--员工数
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--员工表
CREATE TABLE IF NOT EXISTS employees (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,--姓名
  phone VARCHAR(50),--电话
  password VARCHAR(200),--密码
  token  VARCHAR(200),--密码
  firm_id VARCHAR(200),--律所id
  firm_name VARCHAR(200),--律所
  client_num  INT DEFAULT 0,--客户数
  case_num INT DEFAULT 0,--案件数
  status INT DEFAULT 0,--状态 0未启用 1启用
  status_name VARCHAR(50) DEFAULT '未启用',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  update_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--套餐表
CREATE TABLE IF NOT EXISTS packages (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,--名称
  content VARCHAR(100) ,--内容描述
  status INT DEFAULT 0,--状态 0未启用 1启用
  status_name VARCHAR(50) DEFAULT '未启用',
  money  DECIMAL(10,2)    DEFAULT 0,
  day_use_num INT DEFAULT 0,--每日可使用的次数
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--套餐订阅表
CREATE TABLE IF NOT EXISTS packages_user (
  id SERIAL PRIMARY KEY,
  packages_id INT  NOT NULL,--名称
  firms_id  INT  NOT NULL,--律所
  status INT DEFAULT 0,--状态 0未到期 1已到期
  status_name VARCHAR(50) DEFAULT '未到期',
  day_use_num INT DEFAULT 0,--每日可使用的次数
  expiry_date TIMESTAMP  NOT NULL ,--到期时间
  money  DECIMAL(10,2)    DEFAULT 0,--支付金额
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
