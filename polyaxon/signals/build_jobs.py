import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

import auditor

from constants.jobs import JobLifeCycle
from db.models.build_jobs import BuildJob, BuildJobStatus
from event_manager.events.build_job import (
    BUILD_JOB_FAILED,
    BUILD_JOB_NEW_STATUS,
    BUILD_JOB_STOPPED,
    BUILD_JOB_SUCCEEDED
)
from libs.decorators import ignore_raw, ignore_updates
from libs.paths.jobs import delete_job_logs, delete_job_outputs
from polyaxon.celery_api import app as celery_app
from polyaxon.settings import SchedulerCeleryTasks

_logger = logging.getLogger('polyaxon.signals.build_jobs')


@receiver(post_save, sender=BuildJob, dispatch_uid="build_set_post_save")
@ignore_updates
@ignore_raw
def build_set_post_save(sender, **kwargs):
    instance = kwargs['instance']
    instance.set_status(status=JobLifeCycle.CREATED)

    # Clean outputs and logs
    delete_job_logs(instance.unique_name)
    delete_job_outputs(instance.unique_name)


@receiver(post_save, sender=BuildJobStatus, dispatch_uid="build_set_new_status")
@ignore_updates
@ignore_raw
def build_set_new_status(sender, **kwargs):
    instance = kwargs['instance']
    job = instance.job
    previous_status = job.last_status
    # Update job last_status
    job.status = instance
    job.save()
    auditor.record(event_type=BUILD_JOB_NEW_STATUS,
                   instance=job,
                   previous_status=previous_status,
                   target='project')
    if instance.status == JobLifeCycle.STOPPED:
        auditor.record(event_type=BUILD_JOB_STOPPED,
                       instance=job,
                       previous_status=previous_status,
                       target='project')

    if instance.status == JobLifeCycle.FAILED:
        auditor.record(event_type=BUILD_JOB_FAILED,
                       instance=job,
                       previous_status=previous_status,
                       target='project')

    if instance.status == JobLifeCycle.STOPPED:
        auditor.record(event_type=BUILD_JOB_SUCCEEDED,
                       instance=job,
                       previous_status=previous_status,
                       target='project')


@receiver(post_save, sender=BuildJobStatus, dispatch_uid="build_check_stop_job")
@ignore_raw
def build_check_stop_job(sender, **kwargs):
    instance = kwargs['instance']
    build_job_id = instance.job_id

    if instance.status in (JobLifeCycle.FAILED, JobLifeCycle.SUCCEEDED):
        _logger.info('The build job  with id `%s` failed or is done, '
                     'send signal to stop.', build_job_id)
        # Schedule stop for this job
        celery_app.send_task(
            SchedulerCeleryTasks.BUILD_JOBS_STOP,
            kwargs={'build_job_id': build_job_id,
                    'update_status': False})


@receiver(post_save, sender=BuildJobStatus, dispatch_uid="build_handle_done_status")
@ignore_raw
def build_handle_done_status(sender, **kwargs):
    instance = kwargs['instance']
    build_job_id = instance.job_id

    if JobLifeCycle.is_done(instance.status):
        celery_app.send_task(
            SchedulerCeleryTasks.BUILD_JOBS_NOTIFY_DONE,
            kwargs={'build_job_id': build_job_id})
