import logging, datetime

# 定义日志hander
logger = logging.getLogger(__name__)


def task1():
    now = datetime.datetime.now()
    logger.info('task1定时任务在{}已经执行'.format(now))


def task2(now):
    logger.info('task1定时任务在{}已经执行'.format(now))


if __name__ == '__main__':
    task1()
