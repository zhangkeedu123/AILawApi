import asyncio
from datetime import datetime, timedelta
from typing import Optional

from . import package_user_service

_cron_task: Optional[asyncio.Task] = None


async def _update_status_job():
    # 先按到期时间刷新状态
    await package_user_service.bulk_update_status_by_expiry()
    # 每日重置当日使用次数
    await package_user_service.reset_all_day_used()


def _seconds_until_next_1am(now: datetime | None = None) -> float:
    now = now or datetime.now()
    target = now.replace(hour=1, minute=0, second=0, microsecond=0)
    if now >= target:
        target = target + timedelta(days=1)
    return (target - now).total_seconds()


async def _cron_loop():
    # 首次等待至下一个 01:00
    await asyncio.sleep(max(0.0, _seconds_until_next_1am()))
    while True:
        try:
            await _update_status_job()
        except Exception:
            # 保底不中断循环；日志由上层统一处理或后续扩展
            pass
        # 下一次再等待到次日 01:00（重算，防漂移）
        await asyncio.sleep(max(0.0, _seconds_until_next_1am()))


def start_package_user_cron():
    global _cron_task
    if _cron_task is None or _cron_task.done():
        _cron_task = asyncio.create_task(_cron_loop())


def stop_package_user_cron():
    global _cron_task
    if _cron_task and not _cron_task.done():
        _cron_task.cancel()
        _cron_task = None
