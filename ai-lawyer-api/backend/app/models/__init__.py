from ..database import Base
# 导入各模型，让 Alembic 能发现
from .case_model import Case  # noqa
from .client_model import Client  # noqa
from .contract_model import Contract  # noqa
from .document_model import Document  # noqa
from .spider_model import SpiderCustomer  # noqa
from .firm_model import Firm  # noqa
from .employee_model import Employee  # noqa
