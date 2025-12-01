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
  created_user INT DEFAULT 0--创建人

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
   created_user INT DEFAULT 0--创建人
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
  created_user INT DEFAULT 0--创建人
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
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_user INT DEFAULT 0--创建人
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
  role INT DEFAULT 0--权限 0 普通门店 1 管理员
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
  role INT DEFAULT 0--权限 0 员工 1 店长 2 管理员
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
  day_used_num INT DEFAULT 0--每日已使用的次数
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

--文书模板相关



-- 1. 建表
CREATE TABLE IF NOT EXISTS document_template (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,--文书名称
    p_id        INTEGER,--父级id
    url         VARCHAR(500),--地址
    is_template BOOLEAN NOT NULL DEFAULT TRUE,--是否是模板
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP--创建时间
);


-- ==============================================
-- 一、插入一级分类
-- ==============================================
INSERT INTO document_template (name, p_id, is_template) VALUES
    ('民商事', 0, FALSE),
    ('执行', 0, FALSE),
    ('普通行政', 0, FALSE),
    ('刑事自诉', 0, FALSE),
    ('知识产权民事', 0, FALSE),
    ('知识产权行政', 0, FALSE),
    ('环境资源', 0, FALSE),
    ('国家赔偿', 0, FALSE),
    ('海事', 0, FALSE);

-- ==============================================
-- 二、插入二级分类
-- ==============================================

-- 民商事
INSERT INTO document_template (name, p_id, is_template)
SELECT v.name, t.id, FALSE
FROM (VALUES 
    ('离婚纠纷'),('民间借贷纠纷'),('金融借款合同纠纷'),('买卖合同纠纷'),('劳动争议纠纷'),
    ('机动车交通事故责任纠纷'),('银行信用卡纠纷'),('物业服务合同纠纷'),('财产损失保险合同纠纷'),
    ('证券虚假陈述责任纠纷'),('保证保险合同纠纷'),('融资租赁合同纠纷'),('房屋买卖合同纠纷'),
    ('房屋租赁合同纠纷'),('建设工程施工合同纠纷'),('人身保险合同纠纷'),('责任保险合同纠纷')
) AS v(name)
CROSS JOIN document_template t WHERE t.name = '民商事';

-- 执行（严格按您给的9项）
INSERT INTO document_template (name, p_id, is_template)
SELECT v.name, t.id, FALSE
FROM (VALUES 
    ('强制执行申请书'),
    ('暂时解除乘坐飞机、高铁限制措施申请书'),
    ('参与分配申请书'),
    ('执行担保申请书'),
    ('确认优先购买权申请书'),
    ('执行异议申请书'),
    ('执行复议申请书'),
    ('执行监督申请书'),
    ('申请不予执行仲裁裁决、调解书或公证债权文书申请书')
) AS v(name)
CROSS JOIN document_template t WHERE t.name = '执行';

-- 普通行政
INSERT INTO document_template (name, p_id, is_template)
SELECT v.name, t.id, FALSE
FROM (VALUES 
    ('行政处罚'),('行政强制执行'),('行政许可'),('国有土地上房屋征收决定'),
    ('工伤保险资格或者待遇认定'),('政府信息公开'),('行政复议'),('行政协议'),
    ('行政补偿'),('行政赔偿'),('不履行法定职责'),('行政答辩状')
) AS v(name)
CROSS JOIN document_template t WHERE t.name = '普通行政';

-- 刑事自诉
INSERT INTO document_template (name, p_id, is_template)
SELECT v.name, t.id, FALSE
FROM (VALUES ('侮辱案'),('诽谤案'),('重婚案'),('拒不执行判决')) AS v(name)
CROSS JOIN document_template t WHERE t.name = '刑事自诉';

-- 知识产权民事
INSERT INTO document_template (name, p_id, is_template)
SELECT v.name, t.id, FALSE
FROM (VALUES 
    ('侵害商标权纠纷'),('侵害发明专利权纠纷'),('侵害外观设计专利权纠纷'),
    ('侵害植物新品种权纠纷'),('侵害著作权及邻接权纠纷'),('技术合同纠纷'),
    ('不正当竞争纠纷'),('垄断纠纷民事'),('侵害商业秘密纠纷')
) AS v(name)
CROSS JOIN document_template t WHERE t.name = '知识产权民事';

-- 知识产权行政
INSERT INTO document_template (name, p_id, is_template)
SELECT v.name, t.id, FALSE
FROM (VALUES 
    ('商标申请驳回复审纠纷'),('商标撤销复审行政纠纷'),('商标无效行政纠纷'),
    ('专利申请驳回复审行政纠纷'),('专利无效行政纠纷'),('垄断纠纷行政')
) AS v(name)
CROSS JOIN document_template t WHERE t.name = '知识产权行政';

-- 环境资源
INSERT INTO document_template (name, p_id, is_template)
SELECT v.name, t.id, FALSE
FROM (VALUES 
    ('环境污染民事公益诉讼'),('生态破坏民事公益诉讼'),('生态环境损害赔偿诉讼')
) AS v(name)
CROSS JOIN document_template t WHERE t.name = '环境资源';

-- 国家赔偿
INSERT INTO document_template (name, p_id, is_template)
SELECT v.name, t.id, FALSE
FROM (VALUES 
    ('违法刑事拘留赔偿'),('刑事改判无罪赔偿'),
    ('怠于履行监管职责致伤致死赔偿'),('错误执行赔偿')
) AS v(name)
CROSS JOIN document_template t WHERE t.name = '国家赔偿';

-- 海事
INSERT INTO document_template (name, p_id, is_template)
SELECT v.name, t.id, FALSE
FROM (VALUES 
    ('船舶碰撞损害责任纠纷'),('海上、通海水域人身损害责任纠纷'),
    ('海上、通海水域货运代理合同纠纷'),('船员劳务合同纠纷')
) AS v(name)
CROSS JOIN document_template t WHERE t.name = '海事';

-- ==============================================
-- 三、插入三级文书（共 196 条）
-- ==============================================

-- ★★★ 民商事（17 项 × 4 = 68 条）★★★

-- 离婚纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '离婚纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '民商事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '离婚纠纷答辩状.docx', id, '/templates/divorce/defense.docx', TRUE FROM p UNION ALL
SELECT '离婚纠纷答辩状实例.docx', id, '/templates/divorce/defense_example.docx', FALSE FROM p UNION ALL
SELECT '离婚纠纷起诉状.docx', id, '/templates/divorce/complaint.docx', TRUE FROM p UNION ALL
SELECT '离婚纠纷起诉状实例.docx', id, '/templates/divorce/complaint_example.docx', FALSE FROM p;

-- 民间借贷纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '民间借贷纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '民商事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '民间借贷纠纷答辩状.docx', id, '/templates/loan/defense.docx', TRUE FROM p UNION ALL
SELECT '民间借贷纠纷答辩状实例.docx', id, '/templates/loan/defense_example.docx', FALSE FROM p UNION ALL
SELECT '民间借贷纠纷起诉状.docx', id, '/templates/loan/complaint.docx', TRUE FROM p UNION ALL
SELECT '民间借贷纠纷起诉状实例.docx', id, '/templates/loan/complaint_example.docx', FALSE FROM p;

-- 金融借款合同纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '金融借款合同纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '民商事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '金融借款合同纠纷答辩状.docx', id, '/templates/finance_loan/defense.docx', TRUE FROM p UNION ALL
SELECT '金融借款合同纠纷答辩状实例.docx', id, '/templates/finance_loan/defense_example.docx', FALSE FROM p UNION ALL
SELECT '金融借款合同纠纷起诉状.docx', id, '/templates/finance_loan/complaint.docx', TRUE FROM p UNION ALL
SELECT '金融借款合同纠纷起诉状实例.docx', id, '/templates/finance_loan/complaint_example.docx', FALSE FROM p;

-- 买卖合同纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '买卖合同纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '民商事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '买卖合同纠纷答辩状.docx', id, '/templates/sale/defense.docx', TRUE FROM p UNION ALL
SELECT '买卖合同纠纷答辩状实例.docx', id, '/templates/sale/defense_example.docx', FALSE FROM p UNION ALL
SELECT '买卖合同纠纷起诉状.docx', id, '/templates/sale/complaint.docx', TRUE FROM p UNION ALL
SELECT '买卖合同纠纷起诉状实例.docx', id, '/templates/sale/complaint_example.docx', FALSE FROM p;

-- 劳动争议纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '劳动争议纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '民商事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '劳动争议纠纷答辩状.docx', id, '/templates/labor/defense.docx', TRUE FROM p UNION ALL
SELECT '劳动争议纠纷答辩状实例.docx', id, '/templates/labor/defense_example.docx', FALSE FROM p UNION ALL
SELECT '劳动争议纠纷起诉状.docx', id, '/templates/labor/complaint.docx', TRUE FROM p UNION ALL
SELECT '劳动争议纠纷起诉状实例.docx', id, '/templates/labor/complaint_example.docx', FALSE FROM p;

-- 机动车交通事故责任纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '机动车交通事故责任纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '民商事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '机动车交通事故责任纠纷答辩状.docx', id, '/templates/traffic/defense.docx', TRUE FROM p UNION ALL
SELECT '机动车交通事故责任纠纷答辩状实例.docx', id, '/templates/traffic/defense_example.docx', FALSE FROM p UNION ALL
SELECT '机动车交通事故责任纠纷起诉状.docx', id, '/templates/traffic/complaint.docx', TRUE FROM p UNION ALL
SELECT '机动车交通事故责任纠纷起诉状实例.docx', id, '/templates/traffic/complaint_example.docx', FALSE FROM p;

-- 银行信用卡纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '银行信用卡纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '民商事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '银行信用卡纠纷答辩状.docx', id, '/templates/credit/defense.docx', TRUE FROM p UNION ALL
SELECT '银行信用卡纠纷答辩状实例.docx', id, '/templates/credit/defense_example.docx', FALSE FROM p UNION ALL
SELECT '银行信用卡纠纷起诉状.docx', id, '/templates/credit/complaint.docx', TRUE FROM p UNION ALL
SELECT '银行信用卡纠纷起诉状实例.docx', id, '/templates/credit/complaint_example.docx', FALSE FROM p;

-- 物业服务合同纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '物业服务合同纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '民商事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '物业服务合同纠纷答辩状.docx', id, '/templates/property/defense.docx', TRUE FROM p UNION ALL
SELECT '物业服务合同纠纷答辩状实例.docx', id, '/templates/property/defense_example.docx', FALSE FROM p UNION ALL
SELECT '物业服务合同纠纷起诉状.docx', id, '/templates/property/complaint.docx', TRUE FROM p UNION ALL
SELECT '物业服务合同纠纷起诉状实例.docx', id, '/templates/property/complaint_example.docx', FALSE FROM p;

-- 财产损失保险合同纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '财产损失保险合同纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '民商事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '财产损失保险合同纠纷答辩状.docx', id, '/templates/property_ins/defense.docx', TRUE FROM p UNION ALL
SELECT '财产损失保险合同纠纷答辩状实例.docx', id, '/templates/property_ins/defense_example.docx', FALSE FROM p UNION ALL
SELECT '财产损失保险合同纠纷起诉状.docx', id, '/templates/property_ins/complaint.docx', TRUE FROM p UNION ALL
SELECT '财产损失保险合同纠纷起诉状实例.docx', id, '/templates/property_ins/complaint_example.docx', FALSE FROM p;

-- 证券虚假陈述责任纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '证券虚假陈述责任纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '民商事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '证券虚假陈述责任纠纷答辩状.docx', id, '/templates/securities/defense.docx', TRUE FROM p UNION ALL
SELECT '证券虚假陈述责任纠纷答辩状实例.docx', id, '/templates/securities/defense_example.docx', FALSE FROM p UNION ALL
SELECT '证券虚假陈述责任纠纷起诉状.docx', id, '/templates/securities/complaint.docx', TRUE FROM p UNION ALL
SELECT '证券虚假陈述责任纠纷起诉状实例.docx', id, '/templates/securities/complaint_example.docx', FALSE FROM p;

-- 保证保险合同纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '保证保险合同纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '民商事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '保证保险合同纠纷答辩状.docx', id, '/templates/guarantee_ins/defense.docx', TRUE FROM p UNION ALL
SELECT '保证保险合同纠纷答辩状实例.docx', id, '/templates/guarantee_ins/defense_example.docx', FALSE FROM p UNION ALL
SELECT '保证保险合同纠纷起诉状.docx', id, '/templates/guarantee_ins/complaint.docx', TRUE FROM p UNION ALL
SELECT '保证保险合同纠纷起诉状实例.docx', id, '/templates/guarantee_ins/complaint_example.docx', FALSE FROM p;

-- 融资租赁合同纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '融资租赁合同纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '民商事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '融资租赁合同纠纷答辩状.docx', id, '/templates/lease/defense.docx', TRUE FROM p UNION ALL
SELECT '融资租赁合同纠纷答辩状实例.docx', id, '/templates/lease/defense_example.docx', FALSE FROM p UNION ALL
SELECT '融资租赁合同纠纷起诉状.docx', id, '/templates/lease/complaint.docx', TRUE FROM p UNION ALL
SELECT '融资租赁合同纠纷起诉状实例.docx', id, '/templates/lease/complaint_example.docx', FALSE FROM p;

-- 房屋买卖合同纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '房屋买卖合同纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '民商事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '房屋买卖合同纠纷答辩状.docx', id, '/templates/house_sale/defense.docx', TRUE FROM p UNION ALL
SELECT '房屋买卖合同纠纷答辩状实例.docx', id, '/templates/house_sale/defense_example.docx', FALSE FROM p UNION ALL
SELECT '房屋买卖合同纠纷起诉状.docx', id, '/templates/house_sale/complaint.docx', TRUE FROM p UNION ALL
SELECT '房屋买卖合同纠纷起诉状实例.docx', id, '/templates/house_sale/complaint_example.docx', FALSE FROM p;

-- 房屋租赁合同纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '房屋租赁合同纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '民商事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '房屋租赁合同纠纷答辩状.docx', id, '/templates/house_lease/defense.docx', TRUE FROM p UNION ALL
SELECT '房屋租赁合同纠纷答辩状实例.docx', id, '/templates/house_lease/defense_example.docx', FALSE FROM p UNION ALL
SELECT '房屋租赁合同纠纷起诉状.docx', id, '/templates/house_lease/complaint.docx', TRUE FROM p UNION ALL
SELECT '房屋租赁合同纠纷起诉状实例.docx', id, '/templates/house_lease/complaint_example.docx', FALSE FROM p;

-- 建设工程施工合同纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '建设工程施工合同纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '民商事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '建设工程施工合同纠纷答辩状.docx', id, '/templates/construction/defense.docx', TRUE FROM p UNION ALL
SELECT '建设工程施工合同纠纷答辩状实例.docx', id, '/templates/construction/defense_example.docx', FALSE FROM p UNION ALL
SELECT '建设工程施工合同纠纷起诉状.docx', id, '/templates/construction/complaint.docx', TRUE FROM p UNION ALL
SELECT '建设工程施工合同纠纷起诉状实例.docx', id, '/templates/construction/complaint_example.docx', FALSE FROM p;

-- 人身保险合同纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '人身保险合同纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '民商事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '人身保险合同纠纷答辩状.docx', id, '/templates/life_ins/defense.docx', TRUE FROM p UNION ALL
SELECT '人身保险合同纠纷答辩状实例.docx', id, '/templates/life_ins/defense_example.docx', FALSE FROM p UNION ALL
SELECT '人身保险合同纠纷起诉状.docx', id, '/templates/life_ins/complaint.docx', TRUE FROM p UNION ALL
SELECT '人身保险合同纠纷起诉状实例.docx', id, '/templates/life_ins/complaint_example.docx', FALSE FROM p;

-- 责任保险合同纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '责任保险合同纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '民商事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '责任保险合同纠纷答辩状.docx', id, '/templates/liability_ins/defense.docx', TRUE FROM p UNION ALL
SELECT '责任保险合同纠纷答辩状实例.docx', id, '/templates/liability_ins/defense_example.docx', FALSE FROM p UNION ALL
SELECT '责任保险合同纠纷起诉状.docx', id, '/templates/liability_ins/complaint.docx', TRUE FROM p UNION ALL
SELECT '责任保险合同纠纷起诉状实例.docx', id, '/templates/liability_ins/complaint_example.docx', FALSE FROM p;

-- ★★★ 执行（9 项 × 2 = 18 条）★★★
WITH exec_items AS (
    SELECT name FROM (VALUES 
        ('强制执行申请书'),
        ('暂时解除乘坐飞机、高铁限制措施申请书'),
        ('参与分配申请书'),
        ('执行担保申请书'),
        ('确认优先购买权申请书'),
        ('执行异议申请书'),
        ('执行复议申请书'),
        ('执行监督申请书'),
        ('申请不予执行仲裁裁决、调解书或公证债权文书申请书')
    ) AS v(name)
),
parents AS (
    SELECT ei.name, dt.id AS p_id
    FROM exec_items ei
    JOIN document_template dt_parent ON dt_parent.name = '执行'
    JOIN document_template dt ON dt.p_id = dt_parent.id AND dt.name = ei.name
)
INSERT INTO document_template (name, p_id, url, is_template)
SELECT p.name || '.docx', p.p_id, '/templates/exec/' || replace(p.name, ' ', '_') || '.docx', TRUE FROM parents p
UNION ALL
SELECT p.name || '实例.docx', p.p_id, '/templates/exec/' || replace(p.name, ' ', '_') || '_example.docx', FALSE FROM parents p;

-- ★★★ 普通行政（12 项 × 4 = 48 条）★★★
-- 行政处罚
WITH p AS (SELECT id FROM document_template WHERE name = '行政处罚' AND p_id = (SELECT id FROM document_template WHERE name = '普通行政'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '行政处罚行政起诉状.docx', id, '/templates/admin_penalty/complaint.docx', TRUE FROM p UNION ALL
SELECT '行政处罚行政起诉状实例.docx', id, '/templates/admin_penalty/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '行政处罚行政答辩状.docx', id, '/templates/admin_penalty/defense.docx', TRUE FROM p UNION ALL
SELECT '行政处罚行政答辩状实例.docx', id, '/templates/admin_penalty/defense_example.docx', FALSE FROM p;

-- 行政强制执行
WITH p AS (SELECT id FROM document_template WHERE name = '行政强制执行' AND p_id = (SELECT id FROM document_template WHERE name = '普通行政'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '行政强制执行行政起诉状.docx', id, '/templates/admin_force/complaint.docx', TRUE FROM p UNION ALL
SELECT '行政强制执行行政起诉状实例.docx', id, '/templates/admin_force/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '行政强制执行行政答辩状.docx', id, '/templates/admin_force/defense.docx', TRUE FROM p UNION ALL
SELECT '行政强制执行行政答辩状实例.docx', id, '/templates/admin_force/defense_example.docx', FALSE FROM p;

-- 行政许可
WITH p AS (SELECT id FROM document_template WHERE name = '行政许可' AND p_id = (SELECT id FROM document_template WHERE name = '普通行政'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '行政许可行政起诉状.docx', id, '/templates/admin_permit/complaint.docx', TRUE FROM p UNION ALL
SELECT '行政许可行政起诉状实例.docx', id, '/templates/admin_permit/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '行政许可行政答辩状.docx', id, '/templates/admin_permit/defense.docx', TRUE FROM p UNION ALL
SELECT '行政许可行政答辩状实例.docx', id, '/templates/admin_permit/defense_example.docx', FALSE FROM p;

-- 国有土地上房屋征收决定
WITH p AS (SELECT id FROM document_template WHERE name = '国有土地上房屋征收决定' AND p_id = (SELECT id FROM document_template WHERE name = '普通行政'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '房屋征收行政起诉状.docx', id, '/templates/admin_expropriation/complaint.docx', TRUE FROM p UNION ALL
SELECT '房屋征收行政起诉状实例.docx', id, '/templates/admin_expropriation/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '房屋征收行政答辩状.docx', id, '/templates/admin_expropriation/defense.docx', TRUE FROM p UNION ALL
SELECT '房屋征收行政答辩状实例.docx', id, '/templates/admin_expropriation/defense_example.docx', FALSE FROM p;

-- 工伤保险资格或者待遇认定
WITH p AS (SELECT id FROM document_template WHERE name = '工伤保险资格或者待遇认定' AND p_id = (SELECT id FROM document_template WHERE name = '普通行政'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '工伤认定行政起诉状.docx', id, '/templates/admin_injury/complaint.docx', TRUE FROM p UNION ALL
SELECT '工伤认定行政起诉状实例.docx', id, '/templates/admin_injury/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '工伤认定行政答辩状.docx', id, '/templates/admin_injury/defense.docx', TRUE FROM p UNION ALL
SELECT '工伤认定行政答辩状实例.docx', id, '/templates/admin_injury/defense_example.docx', FALSE FROM p;

-- 政府信息公开
WITH p AS (SELECT id FROM document_template WHERE name = '政府信息公开' AND p_id = (SELECT id FROM document_template WHERE name = '普通行政'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '政府信息公开行政起诉状.docx', id, '/templates/admin_info/complaint.docx', TRUE FROM p UNION ALL
SELECT '政府信息公开行政起诉状实例.docx', id, '/templates/admin_info/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '政府信息公开行政答辩状.docx', id, '/templates/admin_info/defense.docx', TRUE FROM p UNION ALL
SELECT '政府信息公开行政答辩状实例.docx', id, '/templates/admin_info/defense_example.docx', FALSE FROM p;

-- 行政复议
WITH p AS (SELECT id FROM document_template WHERE name = '行政复议' AND p_id = (SELECT id FROM document_template WHERE name = '普通行政'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '行政复议申请书.docx', id, '/templates/admin_review/apply.docx', TRUE FROM p UNION ALL
SELECT '行政复议申请书实例.docx', id, '/templates/admin_review/apply_example.docx', FALSE FROM p UNION ALL
SELECT '行政复议答复书.docx', id, '/templates/admin_review/reply.docx', TRUE FROM p UNION ALL
SELECT '行政复议答复书实例.docx', id, '/templates/admin_review/reply_example.docx', FALSE FROM p;

-- 行政协议
WITH p AS (SELECT id FROM document_template WHERE name = '行政协议' AND p_id = (SELECT id FROM document_template WHERE name = '普通行政'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '行政协议纠纷行政起诉状.docx', id, '/templates/admin_agreement/complaint.docx', TRUE FROM p UNION ALL
SELECT '行政协议纠纷行政起诉状实例.docx', id, '/templates/admin_agreement/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '行政协议纠纷行政答辩状.docx', id, '/templates/admin_agreement/defense.docx', TRUE FROM p UNION ALL
SELECT '行政协议纠纷行政答辩状实例.docx', id, '/templates/admin_agreement/defense_example.docx', FALSE FROM p;

-- 行政补偿
WITH p AS (SELECT id FROM document_template WHERE name = '行政补偿' AND p_id = (SELECT id FROM document_template WHERE name = '普通行政'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '行政补偿行政起诉状.docx', id, '/templates/admin_comp/complaint.docx', TRUE FROM p UNION ALL
SELECT '行政补偿行政起诉状实例.docx', id, '/templates/admin_comp/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '行政补偿行政答辩状.docx', id, '/templates/admin_comp/defense.docx', TRUE FROM p UNION ALL
SELECT '行政补偿行政答辩状实例.docx', id, '/templates/admin_comp/defense_example.docx', FALSE FROM p;

-- 行政赔偿
WITH p AS (SELECT id FROM document_template WHERE name = '行政赔偿' AND p_id = (SELECT id FROM document_template WHERE name = '普通行政'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '行政赔偿行政起诉状.docx', id, '/templates/admin_compensate/complaint.docx', TRUE FROM p UNION ALL
SELECT '行政赔偿行政起诉状实例.docx', id, '/templates/admin_compensate/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '行政赔偿行政答辩状.docx', id, '/templates/admin_compensate/defense.docx', TRUE FROM p UNION ALL
SELECT '行政赔偿行政答辩状实例.docx', id, '/templates/admin_compensate/defense_example.docx', FALSE FROM p;

-- 不履行法定职责
WITH p AS (SELECT id FROM document_template WHERE name = '不履行法定职责' AND p_id = (SELECT id FROM document_template WHERE name = '普通行政'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '不履行法定职责行政起诉状.docx', id, '/templates/admin_duty/complaint.docx', TRUE FROM p UNION ALL
SELECT '不履行法定职责行政起诉状实例.docx', id, '/templates/admin_duty/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '不履行法定职责行政答辩状.docx', id, '/templates/admin_duty/defense.docx', TRUE FROM p UNION ALL
SELECT '不履行法定职责行政答辩状实例.docx', id, '/templates/admin_duty/defense_example.docx', FALSE FROM p;

-- 先补：2级节点「行政答辩状」
INSERT INTO document_template (name, p_id, is_template)
SELECT '行政答辩状', id, FALSE
FROM document_template 
WHERE name = '普通行政';

-- 再插：3级文书（挂「行政答辩状」下）
WITH p AS (
    SELECT id 
    FROM document_template 
    WHERE name = '行政答辩状' 
      AND p_id = (SELECT id FROM document_template WHERE name = '普通行政')
)
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '行政答辩状.docx', id, '/templates/admin/general_defense.docx', TRUE FROM p
UNION ALL
SELECT '行政答辩状实例.docx', id, '/templates/admin/general_defense_example.docx', FALSE FROM p;

-- ★★★ 刑事自诉（4 项 × 4 = 16 条）★★★
-- 侮辱案
WITH p AS (SELECT id FROM document_template WHERE name = '侮辱案' AND p_id = (SELECT id FROM document_template WHERE name = '刑事自诉'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '侮辱案刑事自诉状.docx', id, '/templates/criminal/insult_complaint.docx', TRUE FROM p UNION ALL
SELECT '侮辱案刑事自诉状实例.docx', id, '/templates/criminal/insult_complaint_example.docx', FALSE FROM p UNION ALL
SELECT '侮辱案刑事答辩状.docx', id, '/templates/criminal/insult_defense.docx', TRUE FROM p UNION ALL
SELECT '侮辱案刑事答辩状实例.docx', id, '/templates/criminal/insult_defense_example.docx', FALSE FROM p;

-- 诽谤案
WITH p AS (SELECT id FROM document_template WHERE name = '诽谤案' AND p_id = (SELECT id FROM document_template WHERE name = '刑事自诉'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '诽谤案刑事自诉状.docx', id, '/templates/criminal/defamation_complaint.docx', TRUE FROM p UNION ALL
SELECT '诽谤案刑事自诉状实例.docx', id, '/templates/criminal/defamation_complaint_example.docx', FALSE FROM p UNION ALL
SELECT '诽谤案刑事答辩状.docx', id, '/templates/criminal/defamation_defense.docx', TRUE FROM p UNION ALL
SELECT '诽谤案刑事答辩状实例.docx', id, '/templates/criminal/defamation_defense_example.docx', FALSE FROM p;

-- 重婚案
WITH p AS (SELECT id FROM document_template WHERE name = '重婚案' AND p_id = (SELECT id FROM document_template WHERE name = '刑事自诉'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '重婚案刑事自诉状.docx', id, '/templates/criminal/bigamy_complaint.docx', TRUE FROM p UNION ALL
SELECT '重婚案刑事自诉状实例.docx', id, '/templates/criminal/bigamy_complaint_example.docx', FALSE FROM p UNION ALL
SELECT '重婚案刑事答辩状.docx', id, '/templates/criminal/bigamy_defense.docx', TRUE FROM p UNION ALL
SELECT '重婚案刑事答辩状实例.docx', id, '/templates/criminal/bigamy_defense_example.docx', FALSE FROM p;

-- 拒不执行判决
WITH p AS (SELECT id FROM document_template WHERE name = '拒不执行判决' AND p_id = (SELECT id FROM document_template WHERE name = '刑事自诉'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '拒不执行判决刑事自诉状.docx', id, '/templates/criminal/refuse_judgment_complaint.docx', TRUE FROM p UNION ALL
SELECT '拒不执行判决刑事自诉状实例.docx', id, '/templates/criminal/refuse_judgment_complaint_example.docx', FALSE FROM p UNION ALL
SELECT '拒不执行判决刑事答辩状.docx', id, '/templates/criminal/refuse_judgment_defense.docx', TRUE FROM p UNION ALL
SELECT '拒不执行判决刑事答辩状实例.docx', id, '/templates/criminal/refuse_judgment_defense_example.docx', FALSE FROM p;

-- ★★★ 知识产权民事（9 项 × 4 = 36 条）★★★

-- 侵害商标权纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '侵害商标权纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '知识产权民事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '侵害商标权纠纷起诉状.docx', id, '/templates/ip_tm/complaint.docx', TRUE FROM p UNION ALL
SELECT '侵害商标权纠纷起诉状实例.docx', id, '/templates/ip_tm/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '侵害商标权纠纷答辩状.docx', id, '/templates/ip_tm/defense.docx', TRUE FROM p UNION ALL
SELECT '侵害商标权纠纷答辩状实例.docx', id, '/templates/ip_tm/defense_example.docx', FALSE FROM p;

-- 侵害发明专利权纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '侵害发明专利权纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '知识产权民事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '侵害发明专利权纠纷起诉状.docx', id, '/templates/ip_patent/complaint.docx', TRUE FROM p UNION ALL
SELECT '侵害发明专利权纠纷起诉状实例.docx', id, '/templates/ip_patent/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '侵害发明专利权纠纷答辩状.docx', id, '/templates/ip_patent/defense.docx', TRUE FROM p UNION ALL
SELECT '侵害发明专利权纠纷答辩状实例.docx', id, '/templates/ip_patent/defense_example.docx', FALSE FROM p;

-- 侵害外观设计专利权纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '侵害外观设计专利权纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '知识产权民事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '侵害外观设计专利权纠纷起诉状.docx', id, '/templates/ip_design/complaint.docx', TRUE FROM p UNION ALL
SELECT '侵害外观设计专利权纠纷起诉状实例.docx', id, '/templates/ip_design/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '侵害外观设计专利权纠纷答辩状.docx', id, '/templates/ip_design/defense.docx', TRUE FROM p UNION ALL
SELECT '侵害外观设计专利权纠纷答辩状实例.docx', id, '/templates/ip_design/defense_example.docx', FALSE FROM p;

-- 侵害植物新品种权纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '侵害植物新品种权纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '知识产权民事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '侵害植物新品种权纠纷起诉状.docx', id, '/templates/ip_plant/complaint.docx', TRUE FROM p UNION ALL
SELECT '侵害植物新品种权纠纷起诉状实例.docx', id, '/templates/ip_plant/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '侵害植物新品种权纠纷答辩状.docx', id, '/templates/ip_plant/defense.docx', TRUE FROM p UNION ALL
SELECT '侵害植物新品种权纠纷答辩状实例.docx', id, '/templates/ip_plant/defense_example.docx', FALSE FROM p;

-- 侵害著作权及邻接权纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '侵害著作权及邻接权纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '知识产权民事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '侵害著作权纠纷起诉状.docx', id, '/templates/ip_copyright/complaint.docx', TRUE FROM p UNION ALL
SELECT '侵害著作权纠纷起诉状实例.docx', id, '/templates/ip_copyright/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '侵害著作权纠纷答辩状.docx', id, '/templates/ip_copyright/defense.docx', TRUE FROM p UNION ALL
SELECT '侵害著作权纠纷答辩状实例.docx', id, '/templates/ip_copyright/defense_example.docx', FALSE FROM p;

-- 技术合同纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '技术合同纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '知识产权民事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '技术合同纠纷起诉状.docx', id, '/templates/ip_tech/complaint.docx', TRUE FROM p UNION ALL
SELECT '技术合同纠纷起诉状实例.docx', id, '/templates/ip_tech/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '技术合同纠纷答辩状.docx', id, '/templates/ip_tech/defense.docx', TRUE FROM p UNION ALL
SELECT '技术合同纠纷答辩状实例.docx', id, '/templates/ip_tech/defense_example.docx', FALSE FROM p;

-- 不正当竞争纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '不正当竞争纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '知识产权民事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '不正当竞争纠纷起诉状.docx', id, '/templates/ip_unfair/complaint.docx', TRUE FROM p UNION ALL
SELECT '不正当竞争纠纷起诉状实例.docx', id, '/templates/ip_unfair/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '不正当竞争纠纷答辩状.docx', id, '/templates/ip_unfair/defense.docx', TRUE FROM p UNION ALL
SELECT '不正当竞争纠纷答辩状实例.docx', id, '/templates/ip_unfair/defense_example.docx', FALSE FROM p;

-- 垄断纠纷民事
WITH p AS (SELECT id FROM document_template WHERE name = '垄断纠纷民事' AND p_id = (SELECT id FROM document_template WHERE name = '知识产权民事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '垄断纠纷民事起诉状.docx', id, '/templates/ip_monopoly_civil/complaint.docx', TRUE FROM p UNION ALL
SELECT '垄断纠纷民事起诉状实例.docx', id, '/templates/ip_monopoly_civil/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '垄断纠纷民事答辩状.docx', id, '/templates/ip_monopoly_civil/defense.docx', TRUE FROM p UNION ALL
SELECT '垄断纠纷民事答辩状实例.docx', id, '/templates/ip_monopoly_civil/defense_example.docx', FALSE FROM p;

-- 侵害商业秘密纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '侵害商业秘密纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '知识产权民事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '侵害商业秘密纠纷起诉状.docx', id, '/templates/ip_secret/complaint.docx', TRUE FROM p UNION ALL
SELECT '侵害商业秘密纠纷起诉状实例.docx', id, '/templates/ip_secret/complaint_example.docx', FALSE FROM p UNION ALL
SELECT '侵害商业秘密纠纷答辩状.docx', id, '/templates/ip_secret/defense.docx', TRUE FROM p UNION ALL
SELECT '侵害商业秘密纠纷答辩状实例.docx', id, '/templates/ip_secret/defense_example.docx', FALSE FROM p;

-- ★★★ 知识产权行政（6 项 × 4 = 24 条）★★★

-- 商标申请驳回复审纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '商标申请驳回复审纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '知识产权行政'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '商标申请驳回复审纠纷起诉状.docx', id, '/templates/ip_admin/tm_reject_apply.docx', TRUE FROM p UNION ALL
SELECT '商标申请驳回复审纠纷起诉状实例.docx', id, '/templates/ip_admin/tm_reject_apply_example.docx', FALSE FROM p UNION ALL
SELECT '商标申请驳回复审纠纷答辩状.docx', id, '/templates/ip_admin/tm_reject_complaint.docx', TRUE FROM p UNION ALL
SELECT '商标申请驳回复审纠纷答辩状实例.docx', id, '/templates/ip_admin/tm_reject_complaint_example.docx', FALSE FROM p;

-- 商标撤销复审行政纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '商标撤销复审行政纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '知识产权行政'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '商标撤销复审行政纠纷起诉状.docx', id, '/templates/ip_admin/tm_revoke_apply.docx', TRUE FROM p UNION ALL
SELECT '商标撤销复审行政纠纷起诉状实例.docx', id, '/templates/ip_admin/tm_revoke_apply_example.docx', FALSE FROM p UNION ALL
SELECT '第三人意见陈述书(商标撤销复审行政纠纷).docx', id, '/templates/ip_admin/tm_revoke_complaint.docx', TRUE FROM p UNION ALL
SELECT '第三人意见陈述书(商标撤销复审行政纠纷)实例.docx', id, '/templates/ip_admin/tm_revoke_complaint_example.docx', FALSE FROM p;

-- 商标无效行政纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '商标无效行政纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '知识产权行政'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '商标无效行政纠纷起诉状.docx', id, '/templates/ip_admin/tm_invalid_request.docx', TRUE FROM p UNION ALL
SELECT '商标无效行政纠纷起诉状实例.docx', id, '/templates/ip_admin/tm_invalid_request_example.docx', FALSE FROM p UNION ALL
SELECT '第三人意见陈述书(商标无效行政纠纷).docx', id, '/templates/ip_admin/tm_invalid_complaint.docx', TRUE FROM p UNION ALL
SELECT '第三人意见陈述书(商标无效行政纠纷)实例.docx', id, '/templates/ip_admin/tm_invalid_complaint_example.docx', FALSE FROM p;

-- 专利申请驳回复审行政纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '专利申请驳回复审行政纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '知识产权行政'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '专利申请驳回复审行政纠纷起诉状.docx', id, '/templates/ip_admin/patent_reject_request.docx', TRUE FROM p UNION ALL
SELECT '专利申请驳回复审行政纠纷起诉状实例.docx', id, '/templates/ip_admin/patent_reject_request_example.docx', FALSE FROM p ;

-- 专利无效行政纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '专利无效行政纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '知识产权行政'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '专利无效行政纠纷起诉状.docx', id, '/templates/ip_admin/patent_invalid_request.docx', TRUE FROM p UNION ALL
SELECT '专利无效行政纠纷起诉状实例.docx', id, '/templates/ip_admin/patent_invalid_request_example.docx', FALSE FROM p UNION ALL
SELECT '第三人意见陈述书(专利无效行政纠纷).docx', id, '/templates/ip_admin/patent_invalid_complaint.docx', TRUE FROM p UNION ALL
SELECT '第三人意见陈述书(专利无效行政纠纷)起诉状实例.docx', id, '/templates/ip_admin/patent_invalid_complaint_example.docx', FALSE FROM p;

-- 垄断纠纷行政
WITH p AS (SELECT id FROM document_template WHERE name = '垄断纠纷行政' AND p_id = (SELECT id FROM document_template WHERE name = '知识产权行政'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '行政垄断起诉状.docx', id, '/templates/ip_admin/monopoly_admin_complaint.docx', TRUE FROM p UNION ALL
SELECT '行政垄断起诉状实例.docx', id, '/templates/ip_admin/monopoly_admin_complaint_example.docx', FALSE FROM p;

-- ★★★ 环境资源（3 项 × 4 = 12 条）★★★

-- 环境污染民事公益诉讼
WITH p AS (SELECT id FROM document_template WHERE name = '环境污染民事公益诉讼' AND p_id = (SELECT id FROM document_template WHERE name = '环境资源'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '环境污染民事公益诉讼起诉状.docx', id, '/templates/env/pollution_complaint.docx', TRUE FROM p UNION ALL
SELECT '环境污染民事公益诉讼起诉状实例.docx', id, '/templates/env/pollution_complaint_example.docx', FALSE FROM p UNION ALL
SELECT '环境污染民事公益诉讼答辩状.docx', id, '/templates/env/pollution_defense.docx', TRUE FROM p UNION ALL
SELECT '环境污染民事公益诉讼答辩状实例.docx', id, '/templates/env/pollution_defense_example.docx', FALSE FROM p;

-- 生态破坏民事公益诉讼
WITH p AS (SELECT id FROM document_template WHERE name = '生态破坏民事公益诉讼' AND p_id = (SELECT id FROM document_template WHERE name = '环境资源'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '生态破坏民事公益诉讼起诉状.docx', id, '/templates/env/eco_complaint.docx', TRUE FROM p UNION ALL
SELECT '生态破坏民事公益诉讼起诉状实例.docx', id, '/templates/env/eco_complaint_example.docx', FALSE FROM p UNION ALL
SELECT '生态破坏民事公益诉讼答辩状.docx', id, '/templates/env/eco_defense.docx', TRUE FROM p UNION ALL
SELECT '生态破坏民事公益诉讼答辩状实例.docx', id, '/templates/env/eco_defense_example.docx', FALSE FROM p;

-- 生态环境损害赔偿诉讼
WITH p AS (SELECT id FROM document_template WHERE name = '生态环境损害赔偿诉讼' AND p_id = (SELECT id FROM document_template WHERE name = '环境资源'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '生态环境损害赔偿起诉状.docx', id, '/templates/env/compensate_complaint.docx', TRUE FROM p UNION ALL
SELECT '生态环境损害赔偿起诉状实例.docx', id, '/templates/env/compensate_complaint_example.docx', FALSE FROM p UNION ALL
SELECT '生态环境损害赔偿答辩状.docx', id, '/templates/env/compensate_defense.docx', TRUE FROM p UNION ALL
SELECT '生态环境损害赔偿答辩状实例.docx', id, '/templates/env/compensate_defense_example.docx', FALSE FROM p;

-- ★★★ 国家赔偿（4 项 × 4 = 16 条）★★★

-- 违法刑事拘留赔偿
WITH p AS (SELECT id FROM document_template WHERE name = '违法刑事拘留赔偿' AND p_id = (SELECT id FROM document_template WHERE name = '国家赔偿'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '违法刑事拘留赔偿申请书.docx', id, '/templates/state_comp/detain_apply.docx', TRUE FROM p UNION ALL
SELECT '违法刑事拘留赔偿申请书实例.docx', id, '/templates/state_comp/detain_apply_example.docx', FALSE FROM p UNION ALL
SELECT '违法刑事拘留赔偿答辩状.docx', id, '/templates/state_comp/detain_complaint.docx', TRUE FROM p UNION ALL
SELECT '违法刑事拘留赔偿答辩状实例.docx', id, '/templates/state_comp/detain_complaint_example.docx', FALSE FROM p;

-- 刑事改判无罪赔偿
WITH p AS (SELECT id FROM document_template WHERE name = '刑事改判无罪赔偿' AND p_id = (SELECT id FROM document_template WHERE name = '国家赔偿'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '刑事改判无罪赔偿申请书.docx', id, '/templates/state_comp/acquit_apply.docx', TRUE FROM p UNION ALL
SELECT '刑事改判无罪赔偿申请书实例.docx', id, '/templates/state_comp/acquit_apply_example.docx', FALSE FROM p UNION ALL
SELECT '国家赔偿行政赔偿答辩状.docx', id, '/templates/state_comp/acquit_complaint.docx', TRUE FROM p UNION ALL
SELECT '刑事改判无罪赔偿答辩状实例.docx', id, '/templates/state_comp/acquit_complaint_example.docx', FALSE FROM p;

-- 怠于履行监管职责致伤致死赔偿
WITH p AS (SELECT id FROM document_template WHERE name = '怠于履行监管职责致伤致死赔偿' AND p_id = (SELECT id FROM document_template WHERE name = '国家赔偿'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '怠于履行监管职责致伤致死赔偿申请书.docx', id, '/templates/state_comp/duty_apply.docx', TRUE FROM p UNION ALL
SELECT '怠于履行监管职责致伤致死赔偿申请书实例.docx', id, '/templates/state_comp/duty_apply_example.docx', FALSE FROM p UNION ALL
SELECT '怠于履行监管职责致伤致死赔偿答辩状.docx', id, '/templates/state_comp/duty_complaint.docx', TRUE FROM p UNION ALL
SELECT '怠于履行监管职责致伤致死赔偿答辩状实例.docx', id, '/templates/state_comp/duty_complaint_example.docx', FALSE FROM p;

-- 错误执行赔偿
WITH p AS (SELECT id FROM document_template WHERE name = '错误执行赔偿' AND p_id = (SELECT id FROM document_template WHERE name = '国家赔偿'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '错误执行赔偿申请书.docx', id, '/templates/state_comp/exec_apply.docx', TRUE FROM p UNION ALL
SELECT '错误执行赔偿申请书实例.docx', id, '/templates/state_comp/exec_apply_example.docx', FALSE FROM p UNION ALL
SELECT '错误执行赔偿答辩状.docx', id, '/templates/state_comp/exec_complaint.docx', TRUE FROM p UNION ALL
SELECT '错误执行赔偿答辩状实例.docx', id, '/templates/state_comp/exec_complaint_example.docx', FALSE FROM p;

-- ★★★ 海事（4 项 × 4 = 16 条）★★★

-- 船舶碰撞损害责任纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '船舶碰撞损害责任纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '海事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '船舶碰撞损害责任纠纷起诉状.docx', id, '/templates/maritime/collision_complaint.docx', TRUE FROM p UNION ALL
SELECT '船舶碰撞损害责任纠纷起诉状实例.docx', id, '/templates/maritime/collision_complaint_example.docx', FALSE FROM p UNION ALL
SELECT '船舶碰撞损害责任纠纷答辩状.docx', id, '/templates/maritime/collision_defense.docx', TRUE FROM p UNION ALL
SELECT '船舶碰撞损害责任纠纷答辩状实例.docx', id, '/templates/maritime/collision_defense_example.docx', FALSE FROM p;

-- 海上、通海水域人身损害责任纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '海上、通海水域人身损害责任纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '海事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '海上、通海水域人身损害责任纠纷起诉状.docx', id, '/templates/maritime/injury_complaint.docx', TRUE FROM p UNION ALL
SELECT '海上、通海水域人身损害责任纠纷起诉状实例.docx', id, '/templates/maritime/injury_complaint_example.docx', FALSE FROM p UNION ALL
SELECT '海上、通海水域人身损害责任纠纷答辩状.docx', id, '/templates/maritime/injury_defense.docx', TRUE FROM p UNION ALL
SELECT '海上、通海水域人身损害责任纠纷答辩状实例.docx', id, '/templates/maritime/injury_defense_example.docx', FALSE FROM p;

-- 海上、通海水域货运代理合同纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '海上、通海水域货运代理合同纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '海事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '海上、通海水域货运代理合同纠纷起诉状.docx', id, '/templates/maritime/forward_complaint.docx', TRUE FROM p UNION ALL
SELECT '海上、通海水域货运代理合同纠纷起诉状实例.docx', id, '/templates/maritime/forward_complaint_example.docx', FALSE FROM p UNION ALL
SELECT '海上、通海水域货运代理合同纠纷答辩状.docx', id, '/templates/maritime/forward_defense.docx', TRUE FROM p UNION ALL
SELECT '海上、通海水域货运代理合同纠纷答辩状实例.docx', id, '/templates/maritime/forward_defense_example.docx', FALSE FROM p;

-- 船员劳务合同纠纷
WITH p AS (SELECT id FROM document_template WHERE name = '船员劳务合同纠纷' AND p_id = (SELECT id FROM document_template WHERE name = '海事'))
INSERT INTO document_template (name, p_id, url, is_template)
SELECT '船员劳务合同纠纷起诉状.docx', id, '/templates/maritime/crew_complaint.docx', TRUE FROM p UNION ALL
SELECT '船员劳务合同纠纷起诉状实例.docx', id, '/templates/maritime/crew_complaint_example.docx', FALSE FROM p UNION ALL
SELECT '船员劳务合同纠纷答辩状.docx', id, '/templates/maritime/crew_defense.docx', TRUE FROM p UNION ALL
SELECT '船员劳务合同纠纷答辩状实例.docx', id, '/templates/maritime/crew_defense_example.docx', FALSE FROM p;


-- ==============================================

--文书模板相关