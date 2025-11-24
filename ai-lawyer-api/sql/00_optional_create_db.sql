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
  status INT DEFAULT 0,--状态 0 联系中 1已签单
  status_name VARCHAR(50) DEFAULT '联系中',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_user INT DEFAULT 0,--创建人

);

--案件表
CREATE TABLE IF NOT EXISTS cases (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL,--案件名称
  plaintiff VARCHAR(500),--原告
  defendant VARCHAR(500),--被告
  location VARCHAR(200),--法院地址
  status INT DEFAULT 0,--状态 0未受理 1已受理，3.已结案
  status_name VARCHAR(50) DEFAULT '未受理',
  files VARCHAR(2000),--相关文件
  claims VARCHAR(2000),--案件描述
  facts TEXT,--分析结果
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   created_user INT DEFAULT 0,--创建人
);

--文件表
CREATE TABLE IF NOT EXISTS files (
  id SERIAL PRIMARY KEY,
  user_id INT ,--创建用户ID
  name VARCHAR(200) NOT NULL,--文件名称
  doc_url VARCHAR(200) NOT NULL,--文件路径
  content text, --文本内容
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
--合同表
CREATE TABLE IF NOT EXISTS contracts (
  id SERIAL PRIMARY KEY,
  contract_name VARCHAR(200) ,--合同名称
  type VARCHAR(100),--合同类型
  hasrisk VARCHAR(50) ,--是否有风险
  high_risk INT DEFAULT 0,--高风险 
  medium_risk INT DEFAULT 0,--中风险 
  low_risk INT DEFAULT 0,--低风险
  files VARCHAR(200) ,--文件地址
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_user INT DEFAULT 0,--创建人
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
  user_id INT NOT NULL,
  doc_name VARCHAR(200) ,--文书名称
  doc_type VARCHAR(100),--文书类型
  doc_content text,--文件内容
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_user INT DEFAULT 0,--创建人
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
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  role INT DEFAULT 0,--权限 0 普通门店 1 管理员
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
  update_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  role INT DEFAULT 0,--权限 0 员工 1 店长 2 管理员
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
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  day_used_num INT DEFAULT 0,--每日已使用的次数
);

--回话历史记录组
-- conversations & messages schema (PK1: BIGSERIAL)
CREATE TABLE IF NOT EXISTS conversations (
    id          BIGSERIAL PRIMARY KEY,
    user_id     VARCHAR(128) NOT NULL,--用户ID
    title       VARCHAR(256),--标题
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,--如果超出最大token ： false 不可再继续聊天
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id);

--消息
CREATE TABLE IF NOT EXISTS messages (
    id               BIGSERIAL PRIMARY KEY,
    conversation_id  BIGINT ,
    role             VARCHAR(32) ,     -- 'user' | 'assistant'
    content          TEXT ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);


-- 仅保存每个会话的一条摘要，覆盖更新
CREATE TABLE IF NOT EXISTS conversation_summaries (
  id  SERIAL PRIMARY KEY ,
  conversation_id BIGINT ,
  summary         TEXT ,
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversation_summaries_updated_at
  ON conversation_summaries(updated_at DESC);


--营销内容创作相关

-- 1) 选题池 / 创意队列
CREATE TABLE IF NOT EXISTS content_ideas (
  id           SERIAL PRIMARY KEY,
  title        VARCHAR(200) ,                 -- 选题名
  brief        VARCHAR(200),                                  -- 选题简述/切入点
  persona      VARCHAR(100),                          -- 目标读者画像（上班族/企业主/女性当事人等）
  pain_point   VARCHAR(200),                          -- 解决的痛点摘要
  keywords     VARCHAR(200),                               -- 关键词数组
  created_at   TIMESTAMP DEFAULT NOW()
);

-- 2) 风格规范（品牌语气、读者层级、注意/禁忌等）
CREATE TABLE IF NOT EXISTS content_style_guides (
  id             SERIAL PRIMARY KEY,
  tone           VARCHAR(80),                         -- 专业/通俗/亲和/稳重/黑金高端 等
  reading_level  VARCHAR(40),                         -- 受众理解层级提示
  do_list        VARCHAR(500),                               -- 建议遵循点
  dont_list      VARCHAR(500),                                -- 禁用/避免
  legal_scope    VARCHAR(500),                                -- 法域与边界（中国法/特定条线）
  created_at     TIMESTAMP DEFAULT NOW()
);

-- 3) 模板库（结构化片段：标题/开场/要点/法条/CTA）
CREATE TABLE IF NOT EXISTS content_templates (
  id             SERIAL PRIMARY KEY,
  name           VARCHAR(120) ,
  description    VARCHAR(200),--描述
  base_prompt    VARCHAR(500),                       -- 基础提示词（含变量占位）
  created_at     TIMESTAMP DEFAULT NOW()
);

-- 4) 实例化提示词（把选题+风格+变量填充后的 prompt）
CREATE TABLE IF NOT EXISTS content_prompts (
  id             SERIAL PRIMARY KEY,
  filled_prompt  VARCHAR(1000),                       -- 最终投喂模型的提示词
  title     VARCHAR(200)  NULL,   --标题
  employees_id   INT,  --用户id
  created_at     TIMESTAMP DEFAULT NOW()
);

-- 6) 成稿（可用正文）
CREATE TABLE IF NOT EXISTS contents (
  id               SERIAL PRIMARY KEY,
  employees_id     INT  NULL ,--用户id
  title            VARCHAR(200)  NULL,
  body_md          TEXT  NULL,                      -- 正文（建议 Markdown）
  keywords         VARCHAR(200),  
  reading_level    VARCHAR(40),
  tone             VARCHAR(80),
  created_at       TIMESTAMP DEFAULT NOW()
);

-- 1️⃣ 选题池 / 创意队列
INSERT INTO content_ideas (title, brief, persona, pain_point, keywords, created_at) VALUES
('被公司“劝退”，补偿怎么算？', '讲解劳动合同法中N+1补偿机制', '上班族', '签自愿离职被坑，无法获得补偿', '劳动合同法,N+1,经济补偿金,代通知金', NOW()),
('合同违约金能随便写吗？', '违约金过高被法院调低，如何合理约定', '企业主', '合同条款写法不当，赔偿风险高', '违约金,合同法,司法解释,格式条款', NOW()),
('婚内财产协议有效吗？', '普及婚前/婚内财产协议的法律效力', '女性当事人', '签了婚内协议怕不被法院认可', '婚姻法,财产约定,夫妻共同财产,无效条款', NOW()),
('劳务合同与劳动合同区别', '讲解签错合同的法律风险', 'HR从业者', '规避用工风险但错签劳务合同', '劳务关系,劳动合同法,社保,仲裁风险', NOW()),
('离职补偿金计算公式', '科普离职时经济补偿与代通知金计算方式', '职场新人', '被辞退时不知道该拿多少补偿', '劳动仲裁,经济补偿,工龄,工资基数', NOW()),
('公司拖欠工资怎么办？', '普及劳动者讨薪法律途径', '工厂员工', '被拖欠工资但不懂法律维权流程', '拖欠工资,劳动监察,劳动仲裁,民事诉讼', NOW()),
('租赁合同提前解约责任', '讲解提前解约的违约条款处理', '租客/房东', '不清楚提前退租赔偿责任', '租赁合同,违约金,押金,租期条款', NOW()),
('交通事故私了风险', '讲述交通事故私了后可能的法律隐患', '车主', '事故后签私了协议反而吃亏', '交通事故,私了协议,保险理赔,责任认定', NOW()),
('劳动仲裁流程详解', '一步步带你搞懂仲裁流程', '员工', '被辞退但不知道如何提起仲裁', '仲裁流程,仲裁时效,证据准备,申请书', NOW()),
('保密协议怎么签？', '普及保密条款的合理范围与风险', '职场白领', '签保密协议怕限制跳槽', '保密协议,竞业限制,违约责任,劳动合同', NOW());


-- 2️⃣ 风格规范（品牌语气、读者层级、注意/禁忌等）
INSERT INTO content_style_guides (tone, reading_level, do_list, dont_list, legal_scope, created_at) VALUES
('稳重·专业·黑金高端', '大众可读', '使用真实案例；强调法条出处；提供律师建议。', '不要夸大；不要使用“保证赢”字眼；避免对立性表达。', '中国法 - 劳动、合同纠纷', NOW()),
('亲和·通俗·有温度', '通俗易懂', '多用生活化例子；使用问句；给出操作建议。', '避免术语堆砌；避免高冷说教。', '中国法 - 婚姻家庭、民事', NOW()),
('简洁·干练·白皮书风', '专业人群', '列清条款；使用逻辑结构；有引用编号。', '避免口语化；避免情绪词。', '中国法 - 企业合规、合同法', NOW()),
('故事化·情感驱动', '普通大众', '用人物故事引入；结尾有共鸣。', '不虚构案件结果；不传播恐慌。', '中国法 - 劳动仲裁、社会保障', NOW());


-- 3️⃣ 模板库（结构化片段与提示词）
INSERT INTO content_templates (name, description, base_prompt, created_at) VALUES
('公众号科普模板', '适合公众号长文结构，含引入、误区、法条、CTA',
 '请以{tone}风格，面向{persona}，围绕主题「{topic}」撰写公众号文章。要求语言{reading_level}，引用法条并提供律师建议。', NOW()),
('短视频脚本模板', '用于抖音或视频号的快节奏口播脚本',
 '生成主题「{topic}」的视频脚本（目标读者：{persona}，语气：{tone}）：5秒内提出问题，2个场景说明，1句法条总结，结尾CTA提醒咨询。', NOW()),
('图文卡片模板', '用于朋友圈/小红书图文卡片生成',
 '根据主题「{topic}」，输出3个关键要点和1条行动建议，风格：{tone}，阅读层级：{reading_level}。', NOW()),
('案例解析模板', '用于解读判决或典型案例',
 '请以律师视角解析案例「{topic}」，结构包括：案情摘要、争议焦点、法院观点、启示与建议。', NOW()),
('问答模板', '用于知乎或问答型内容生成',
 '回答问题「{topic}」，目标读者：{persona}，要求语言{reading_level}，风格：{tone}，提供专业法条依据与建议。', NOW());



--提示词
INSERT INTO content_prompts (filled_prompt, employees_id, created_at) VALUES
(
 '请以稳重·专业·黑金高端风格，面向上班族，围绕主题「被公司劝退，补偿怎么算？」撰写公众号文章。要求语言大众可读，引用《劳动合同法》第47条并提供律师建议。',
  1, NOW()
),
(
 '生成主题「合同违约金能随便写吗？」的视频脚本（目标读者：企业主，语气：简洁·干练·白皮书风）：5秒内提出问题，2个场景说明，1句法条总结，结尾CTA提醒咨询。',
 1, NOW()
),
(
 '根据主题「婚内财产协议有效吗？」，输出3个关键要点和1条行动建议，风格：亲和·通俗·有温度，阅读层级：通俗易懂。',
  1, NOW()
),
(
 '请以律师视角解析案例「离职补偿金计算公式」，结构包括：案情摘要、争议焦点、法院观点、启示与建议。',
  1, NOW()
),
(
 '回答问题「公司拖欠工资怎么办？」，目标读者：工厂员工，要求语言通俗易懂，风格：故事化·情感驱动，提供劳动监察条例法条依据与维权建议。',
 1, NOW()
),
(
 '请以稳重·专业·黑金高端风格，面向职场新人，围绕主题「离职补偿金怎么算？」撰写公众号文章，引用《劳动合同法》第47条。',
  1, NOW()
),
(
 '生成主题「保密协议怎么签？」的视频脚本（目标读者：职场白领，语气：简洁·干练·白皮书风）：5秒提出问题，解释保密条款三要点，结尾提示跳槽风险。',
  1, NOW()
),
(
 '根据主题「交通事故私了风险」，输出3个关键要点和1条行动建议，风格：亲和·通俗·有温度，阅读层级：大众可读。',
  1, NOW()
),
(
 '请以律师视角解析案例「租赁合同提前解约责任」，结构包括：案情摘要、争议焦点、法院观点、启示与建议。',
  1, NOW()
),
(
 '回答问题「劳动仲裁流程详解」，目标读者：上班族，要求语言稳重，风格：专业，引用劳动仲裁法第27条并给出实操建议。',
  1, NOW()
);



-- 5️⃣ 成稿内容（Markdown 示例）
INSERT INTO contents (employees_id, title, body_md, keywords, reading_level, tone, created_at) VALUES
(1, '被公司劝退补偿怎么算？', 
 '# 被公司“劝退”，补偿怎么算？  
多数员工被“劝退”时签了自愿离职协议，但其实可以主张*N+1*。  
**律师建议：** 保存聊天记录，计算经济补偿金和代通知金。', 
 '劳动合同法,N+1,代通知金,违法解除', '大众可读', '稳重·专业·黑金高端', NOW()),

(1, '合同违约金能随便写吗？', 
 '## 合同违约金的约定规则  
法院通常认为过高的违约金无效，应以实际损失为限。  
**建议：** 合同条款写明依据与计算方式，避免被调低。', 
 '违约金,合同法,民法典', '专业人群', '简洁·干练·白皮书风', NOW()),

(1, '婚内财产协议有效吗？', 
 '### 婚内协议的效力  
协议需双方自愿、明确财产范围并经公证更稳妥。  
**律师建议：** 尽量书面签署并注明适用条款。', 
 '婚姻法,财产协议,公证,夫妻财产', '通俗易懂', '亲和·通俗·有温度', NOW()),

(1, '离职补偿金计算公式', 
 '补偿金=工作年限×月工资，另加未提前通知的一个月代通知金。  
**示例：** 工作5年，月薪8000元 → 补偿金=48000元。', 
 '补偿金,劳动法,工资,计算公式', '大众可读', '稳重·专业·黑金高端', NOW()),

(1, '保密协议怎么签？', 
 '## 保密条款三要点  
1. 明确保密范围；  
2. 约定期限；  
3. 违约责任适度。  
**提示：** 谨防“禁止跳槽”过度限制。', 
 '保密协议,竞业限制,劳动合同', '专业人群', '简洁·干练·白皮书风', NOW());



--营销内容创作相关