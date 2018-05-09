from event_manager.event import Attribute, Event

NOTEBOOK_STARTED = 'notebook.started'
NOTEBOOK_STOPPED = 'notebook.stopped'
NOTEBOOK_VIEWED = 'notebook.viewed'
NOTEBOOK_NEW_STATUS = 'notebook.new_status'


class NotebookStartedEvent(Event):
    event_type = NOTEBOOK_STARTED
    actor_id = 'actor_id'
    attributes = (
        Attribute('id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('actor_id')
    )


class NotebookSoppedEvent(Event):
    event_type = NOTEBOOK_STOPPED
    actor_id = 'actor_id'
    attributes = (
        Attribute('id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('actor_id'),
        Attribute('status'),
    )


class NotebookViewedEvent(Event):
    event_type = NOTEBOOK_VIEWED
    actor_id = 'actor_id'
    attributes = (
        Attribute('id'),
        Attribute('project.id'),
        Attribute('project.user.id'),
        Attribute('actor_id'),
        Attribute('status'),
    )


class NotebookNewStatusEvent(Event):
    event_type = NOTEBOOK_NEW_STATUS
    attributes = (
        Attribute('id'),
        Attribute('project.id'),
        Attribute('status')
    )