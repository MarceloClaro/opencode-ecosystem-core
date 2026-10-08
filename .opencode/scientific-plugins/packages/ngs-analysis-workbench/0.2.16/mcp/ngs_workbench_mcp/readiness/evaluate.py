"""Pure evaluation of binding requirements against runtime observations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

from ngs_workbench_daemon.hashing import sha256_hex

from ..runtime.models import (
    ControllerRuntimeCandidate,
    RuntimeCommand,
    RuntimeEnvironmentSnapshot,
)
from .models import ReadinessAssessment, ReadinessEvidence, RequirementSet, RuntimeRequirement


@dataclass(frozen=True)
class _ControllerSelection:
    """Pure result of selecting a workflow controller from one runtime snapshot."""

    candidate: ControllerRuntimeCandidate | None = None
    blockers: tuple[str, ...] = ()
    unknowns: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


def _status(
    blockers: list[str],
    unknowns: list[str],
) -> Literal["ready", "blocked", "unknown"]:
    if blockers:
        return "blocked"
    if unknowns:
        return "unknown"
    return "ready"


def _command_blocker(requirement: RuntimeRequirement, command: RuntimeCommand) -> str | None:
    if command.state == "ready":
        return None
    if command.state == "missing":
        return f"required executable is not available: {requirement.value}"
    return (
        f"required executable is not usable: {requirement.value} "
        f"({command.message or command.state})"
    )


def _evaluate_command(
    requirement: RuntimeRequirement,
    observations: dict[str, RuntimeCommand],
) -> tuple[list[str], list[str], bool]:
    candidates = requirement.command_candidates()
    observed = [observations[name] for name, _ in candidates if name in observations]
    if not observed:
        return [], [f"runtime did not observe required executable: {requirement.value}"], False
    if requirement.capability == "command_group":
        if any(command.state == "ready" for command in observed):
            return [], [], True
        if len(observed) != len(candidates):
            return (
                [],
                [f"runtime did not observe every executable option: {requirement.value}"],
                False,
            )
        return [f"no compatible executable is usable: {requirement.value}"], [], False

    blocker = _command_blocker(requirement, observed[0])
    return ([blocker] if blocker else []), [], blocker is None


def _evaluate_docker_daemon(snapshot: RuntimeEnvironmentSnapshot) -> str | None:
    if snapshot.docker.endpoint_is_local is False:
        return f"Docker endpoint is not local: {snapshot.docker.endpoint}"
    if not snapshot.docker.daemon_reachable:
        return "Docker daemon is not reachable" + (
            f": {snapshot.docker.message}" if snapshot.docker.message else ""
        )
    return None


def _controller_selection_warnings(
    requirement: RuntimeRequirement,
    candidate: ControllerRuntimeCandidate,
) -> tuple[str, ...]:
    warnings: list[str] = []
    if candidate.source == "host_path":
        warnings.append(
            f"using explicitly selected Host PATH {requirement.value}; its package source "
            "and dependency closure are not reproducibly bound"
        )
    elif candidate.lockfile_path is None:
        warnings.append(
            f"selected managed {requirement.value} environment has no observed lockfile"
        )
    if candidate.platform_matches_host is None:
        warnings.append(f"selected {requirement.value} environment platform could not be verified")
    return tuple(warnings)


def _select_controller(
    requirement: RuntimeRequirement,
    snapshot: RuntimeEnvironmentSnapshot,
    controller_candidate_id: str | None,
) -> _ControllerSelection:
    candidates = [
        candidate
        for candidate in snapshot.controller_candidates
        if candidate.controller == requirement.value
    ]
    if controller_candidate_id is not None:
        selected = next(
            (
                candidate
                for candidate in candidates
                if candidate.candidate_id == controller_candidate_id
            ),
            None,
        )
        if selected is None:
            blocker = (
                "selected controller candidate is not available in this runtime "
                f"snapshot: {controller_candidate_id}"
            )
            return _ControllerSelection(blockers=(blocker,))
        if selected.platform_matches_host is False:
            blocker = (
                f"selected {requirement.value} environment is incompatible with the "
                f"host platform: {selected.environment_path}"
            )
            return _ControllerSelection(
                candidate=selected,
                blockers=(blocker,),
            )
        return _ControllerSelection(
            candidate=selected,
            warnings=_controller_selection_warnings(requirement, selected),
        )

    preferred = [candidate for candidate in candidates if candidate.recommended]
    if len(preferred) == 1:
        selected = preferred[0]
        return _ControllerSelection(
            candidate=selected,
            warnings=_controller_selection_warnings(requirement, selected),
        )
    if len(preferred) > 1:
        candidate_ids = ", ".join(candidate.candidate_id for candidate in preferred)
        unknown = (
            f"multiple recommended {requirement.value} environments are available; "
            f"select one controller_candidate_id: {candidate_ids}"
        )
        return _ControllerSelection(unknowns=(unknown,))

    compatible_fallbacks = [
        candidate for candidate in candidates if candidate.platform_matches_host is not False
    ]
    if compatible_fallbacks:
        candidate_ids = ", ".join(
            f"{candidate.candidate_id} ({candidate.source})" for candidate in compatible_fallbacks
        )
        unknown = (
            f"no recommended managed {requirement.value} environment is available; "
            "obtain user confirmation before selecting a fallback "
            f"controller_candidate_id: {candidate_ids}"
        )
        return _ControllerSelection(unknowns=(unknown,))
    if candidates:
        blocker = f"no {requirement.value} controller candidate matches the host platform"
        return _ControllerSelection(blockers=(blocker,))

    if snapshot.managed_environments.truncated:
        return _ControllerSelection(
            unknowns=(f"managed environment discovery was incomplete for {requirement.value}",)
        )

    observations = {command.name: command for command in snapshot.commands}
    blockers, unknowns, _ = _evaluate_command(requirement, observations)
    return _ControllerSelection(
        blockers=tuple(blockers),
        unknowns=tuple(unknowns),
    )


def _finish(readiness: ReadinessAssessment) -> ReadinessAssessment:
    payload = readiness.model_dump(mode="json", exclude={"readiness_id"})
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    readiness.readiness_id = f"readiness-{sha256_hex(encoded)[:32]}"
    return readiness


def evaluate(
    requirement_set: RequirementSet,
    snapshot: RuntimeEnvironmentSnapshot,
    controller_candidate_id: str | None = None,
) -> ReadinessAssessment:
    """Evaluate requirements without performing probes or resolving binding policy."""
    observations = {command.name: command for command in snapshot.commands}
    blockers = list(requirement_set.blockers)
    unknowns = list(requirement_set.unknowns)
    warnings = [*snapshot.warnings, *requirement_set.warnings]
    ready_executables: set[str] = set()
    selected_controller: ControllerRuntimeCandidate | None = None

    for requirement in requirement_set.requirements:
        if requirement.capability not in {"command", "command_group"}:
            continue
        if requirement.layer == "workflow_controller":
            selection = _select_controller(requirement, snapshot, controller_candidate_id)
            selected_controller = selection.candidate
            blockers.extend(selection.blockers)
            unknowns.extend(selection.unknowns)
            warnings.extend(selection.warnings)
            continue
        if (
            requirement.layer == "task_software"
            and selected_controller is None
            and snapshot.managed_environments.truncated
        ):
            continue
        if (
            requirement.layer == "task_software"
            and selected_controller is not None
            and selected_controller.source == "managed_environment"
        ):
            environment = next(
                (
                    item
                    for item in snapshot.managed_environments.environments
                    if item.path == selected_controller.environment_path
                ),
                None,
            )
            if environment is not None:
                available = {command.name: command for command in environment.commands}
                for name, executable in requirement.command_candidates():
                    observed = available.get(executable)
                    observations[name] = (
                        observed.model_copy(update={"name": name})
                        if observed is not None
                        else RuntimeCommand(name=name, path=None, state="missing")
                    )
            else:
                for name, _ in requirement.command_candidates():
                    observations.pop(name, None)
        command_blockers, command_unknowns, is_ready = _evaluate_command(
            requirement,
            observations,
        )
        blockers.extend(command_blockers)
        unknowns.extend(command_unknowns)
        if is_ready:
            ready_executables.add(requirement.value)

    for requirement in requirement_set.requirements:
        if requirement.capability != "daemon":
            continue
        if requirement.value == "docker":
            if "docker" not in ready_executables:
                continue
            if blocker := _evaluate_docker_daemon(snapshot):
                blockers.append(blocker)
        else:
            unknowns.append(f"runtime daemon observation is unsupported: {requirement.value}")

    readiness_status = _status(blockers, unknowns)
    return _finish(
        ReadinessAssessment(
            ok=readiness_status == "ready",
            status=readiness_status,
            binding=requirement_set.binding,
            pipeline=requirement_set.pipeline,
            target=snapshot.target,
            scope="exact_request_and_runtime_snapshot",
            snapshot_id=snapshot.snapshot_id,
            observed_at=snapshot.observed_at,
            expires_at=snapshot.expires_at,
            host=snapshot.host,
            commands=list(observations.values()),
            controller_candidates=snapshot.controller_candidates,
            selected_controller=selected_controller,
            docker=snapshot.docker,
            requirements=requirement_set.requirements,
            evidence=[
                ReadinessEvidence(
                    kind="runtime_snapshot",
                    source=snapshot.snapshot_id,
                    detail=f"observations for compute target {snapshot.target.target_id}",
                ),
                *requirement_set.evidence,
            ],
            blockers=blockers,
            unknowns=unknowns,
            warnings=warnings,
        )
    )
