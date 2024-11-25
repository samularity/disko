from typing import Any
from disko_lib.action import Action, Plan
from disko_lib.config_type import DiskoConfig
from disko_lib.result import DiskoResult
import disko_lib.types.disk as disk


def _generate_plan_for_changes(
    actions: set[Action], current_status: DiskoConfig, target_config: DiskoConfig
) -> DiskoResult[Plan]:
    # TODO: Add generation for ZFS, MDADM, LVM, etc.
    return disk.generate_plan(actions, current_status, target_config)


def generate_plan(
    actions: set[Action], current_status: DiskoConfig, target_config: DiskoConfig
) -> DiskoResult[Plan]:
    if "destroy" in actions:
        current_status = DiskoConfig(disk={}, lvm_vg={}, mdadm={}, nodev={}, zpool={})

    return _generate_plan_for_changes(actions, current_status, target_config)
