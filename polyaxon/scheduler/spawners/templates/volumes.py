from kubernetes import client

from django.conf import settings

from scheduler.spawners.templates import constants


def get_volume_mount(volume, volume_mount=None):
    return client.V1VolumeMount(name=volume, mount_path=volume_mount)


def get_volume(volume, claim_name=None, volume_mount=None):
    if claim_name:
        pv_claim = client.V1PersistentVolumeClaimVolumeSource(claim_name=claim_name)
        return client.V1Volume(name=volume, persistent_volume_claim=pv_claim)

    if volume_mount:
        return client.V1Volume(
            name=volume,
            host_path=client.V1HostPathVolumeSource(path=volume_mount))

    empty_dir = client.V1EmptyDirVolumeSource()
    return client.V1Volume(name=volume, empty_dir=empty_dir)


def get_pod_volumes():
    volumes = []
    volume_mounts = []
    volumes.append(get_volume(volume=constants.DATA_VOLUME,
                              claim_name=settings.DATA_CLAIM_NAME,
                              volume_mount=settings.DATA_ROOT))
    volume_mounts.append(get_volume_mount(volume=constants.DATA_VOLUME,
                                          volume_mount=settings.DATA_ROOT))

    volumes.append(get_volume(volume=constants.OUTPUTS_VOLUME,
                              claim_name=settings.OUTPUTS_CLAIM_NAME,
                              volume_mount=settings.OUTPUTS_ROOT))
    volume_mounts.append(get_volume_mount(volume=constants.OUTPUTS_VOLUME,
                                          volume_mount=settings.OUTPUTS_ROOT))

    if settings.EXTRA_PERSISTENCES:
        for i, extra_data in enumerate(settings.EXTRA_PERSISTENCES):
            volume_name = 'extra-{}'.format(i)
            mount_path = extra_data.get('mountPath')
            claim_name = extra_data.get('existingClaim')
            host_path = extra_data.get('hostPath')
            if mount_path:
                volumes.append(get_volume(volume=volume_name,
                                          claim_name=claim_name,
                                          volume_mount=host_path))
                volume_mounts.append(get_volume_mount(volume=volume_name,
                                                      volume_mount=mount_path))
    return volumes, volume_mounts


def get_docker_volumes():
    volumes = [get_volume(volume=constants.DOCKER_VOLUME, volume_mount=settings.MOUNT_PATHS_DOCKER)]
    volume_mounts = [get_volume_mount(volume=constants.DOCKER_VOLUME,
                                      volume_mount=settings.MOUNT_PATHS_DOCKER)]
    return volumes, volume_mounts
