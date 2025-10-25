# ✅ AILawyer 项目重构任务：移除 ORM & Alembic，全面改为 asyncpg + SQL（Dapper 风格）

目标：  
本项目当前数据库访问使用 SQLAlchemy ORM 和 Alembic。现需**彻底移除 ORM 相关内容**，替换为 **asyncpg + 手写 SQL（Dapper Style）**，提高性能与可控性。

---

## ✅ 最终要求

- **不使用 ORM**
- **不使用 Alembic**
- **所有 CRUD 改为 asyncpg + SQL**
- **所有 Service 必须使用 Repository 层，不直接写 SQL**
- **API 路由路径与入参/出参保持不变**
- **保留 Pydantic schemas（用于DTO/响应）**
- **仓储命名采用 R1 风格**：`client_repo.py`, `case_repo.py`, `contract_repo.py`, ...
- **数据库迁移改为 SQL 文件方式管理（./sql/*.sql）**

---

## ✅ 已完成模块（不需要 Codex 修改）

| 模块 | 状态 | 技术栈 |
|---------|---------|---------|
| `chat_router.py` | ✅ 已完成 | FastAPI |
| `conversation_service.py` | ✅ 已完成 | asyncpg |
| `repositories/conversations_repo.py` | ✅ 已完成 | asyncpg |
| `repositories/messages_repo.py` | ✅ 已完成 | asyncpg |
| `core/ai_client.py` | ✅ 已完成 | httpx |
| `core/memory_manager.py` | ✅ 已完成 | 内存摘要 |
| `db/db.py` | ✅ 已完成 | asyncpg pool |

> 服务与路由改造请模仿以上模块风格  

---

## ✅ 待改造模块（Codex 需要完成）
并添加适当的注释
### 1）Routers（路径不变，只替换内部 service 调用方式）

路径：`backend/app/routers/`

必须改造的文件：
case_router.py
client_router.py
contract_router.py
document_router.py
employee_router.py
firm_router.py
spider_router.py

要求：
- 不修改 `router = APIRouter(...)` 与 `@router.get/post/...` 路由路径
- 将内部依赖 ORM 的调用替换为对应 Service 方法

---

### 2）Services（使用 asyncpg Repository 替代 ORM）

路径：`backend/app/services/`

需要改造的文件：
case_service.py
client_service.py
contract_service.py
document_service.py
employee_service.py
firm_service.py
spider_service.py

要求：
- 内部方法全部改为 async
- 调用新建的 repo：`from backend.app.db.repositories.client_repo import ...`
- 不保留 ORM session 逻辑
- 不使用 SQLAlchemy 查询语法
- 遵循 CRUD 格式示例：

示例（service调用repo）：
```python
pool = await get_pg_pool()
return await client_repo.get_by_id(pool, id)

backend/app/db/repositories/
这个目录下创建
case_repo.py
client_repo.py
contract_repo.py
document_repo.py
employee_repo.py
firm_repo.py
spider_repo.py

每个 repo 必须包含以下函数（按实际业务可增减）：
async def get_all(pool, skip: int, limit: int) -> list: ...
async def get_by_id(pool, id: int) -> dict | None: ...
async def create(pool, data) -> int: ...
async def update(pool, id: int, data) -> bool: ...
async def delete(pool, id: int) -> bool: ...

SQL需要用 asyncpg 格式，例如：

row = await conn.fetchrow("SELECT * FROM clients WHERE id=$1;", id)

任务完成后，请 Codex 回复 READY。
