from __future__ import annotations

import math
import random
from typing import Any

import numpy as np

from .errors import MissingDependencyError, SimulationError
from .result import quaternion_to_matrix
from .types import BodyPose, MeshData, SimulationFrame, SimulationResult

PHYSICS_HZ = 240
QUIET_LINEAR_SPEED = 0.18
QUIET_ANGULAR_SPEED = 0.35
QUIET_HOLD_SECONDS = 0.25
POST_SETTLE_HOLD_SECONDS = 0.35
TABLE_HALF_EXTENTS = [7.0, 4.5, 0.08]
TABLE_TOP_Z = 0.0


def simulate_roll(
    mesh: MeshData,
    count: int,
    seed: int,
    duration_ms: int,
    fps: int,
) -> SimulationResult:
    p = _load_pybullet()
    rng = random.Random(seed)
    client = p.connect(p.DIRECT)
    bodies: list[int] = []
    try:
        p.resetSimulation(physicsClientId=client)
        p.setGravity(0, 0, -9.81, physicsClientId=client)
        p.setTimeStep(1 / PHYSICS_HZ, physicsClientId=client)
        p.setPhysicsEngineParameter(
            deterministicOverlappingPairs=1,
            fixedTimeStep=1 / PHYSICS_HZ,
            numSolverIterations=80,
            physicsClientId=client,
        )

        table_collision = p.createCollisionShape(
            p.GEOM_BOX,
            halfExtents=TABLE_HALF_EXTENTS,
            physicsClientId=client,
        )
        table_body = p.createMultiBody(
            baseMass=0,
            baseCollisionShapeIndex=table_collision,
            basePosition=[0, 0, TABLE_TOP_Z - TABLE_HALF_EXTENTS[2]],
            physicsClientId=client,
        )
        p.changeDynamics(
            table_body,
            -1,
            lateralFriction=1.35,
            restitution=0.10,
            rollingFriction=0.18,
            spinningFriction=0.16,
            physicsClientId=client,
        )

        collision = p.createCollisionShape(
            shapeType=p.GEOM_MESH,
            vertices=mesh.vertices.tolist(),
            physicsClientId=client,
        )
        visual = p.createVisualShape(
            shapeType=p.GEOM_MESH,
            vertices=mesh.vertices.tolist(),
            indices=mesh.faces.reshape(-1).astype(int).tolist(),
            rgbaColor=[1.0, 1.0, 1.0, 1.0],
            physicsClientId=client,
        )

        spacing = 0.55
        start_x = -3.2 - spacing * (count - 1) / 2
        for idx in range(count):
            position = [
                start_x + idx * spacing + rng.uniform(-0.12, 0.12),
                -0.9 + rng.uniform(-0.18, 0.18),
                1.85 + idx * 0.16,
            ]
            orientation = p.getQuaternionFromEuler(
                [
                    rng.random() * 2 * math.pi,
                    rng.random() * 2 * math.pi,
                    rng.random() * 2 * math.pi,
                ]
            )
            body = p.createMultiBody(
                baseMass=1.0,
                baseCollisionShapeIndex=collision,
                baseVisualShapeIndex=visual,
                basePosition=position,
                baseOrientation=orientation,
                physicsClientId=client,
            )
            p.changeDynamics(
                body,
                -1,
                lateralFriction=1.25,
                restitution=0.12,
                rollingFriction=0.20,
                spinningFriction=0.18,
                linearDamping=0.015,
                angularDamping=0.02,
                physicsClientId=client,
            )
            p.resetBaseVelocity(
                body,
                linearVelocity=[
                    rng.uniform(4.2, 5.4),
                    rng.uniform(0.35, 1.25),
                    rng.uniform(1.1, 2.2),
                ],
                angularVelocity=[
                    rng.uniform(-34.0, 34.0),
                    rng.uniform(-34.0, 34.0),
                    rng.uniform(-34.0, 34.0),
                ],
                physicsClientId=client,
            )
            bodies.append(body)

        frames, settled, settle_time = _capture_until_settled(
            p, client, bodies, duration_ms, fps
        )
        raw_final_poses = tuple(_pose_for_body(p, client, body) for body in bodies)
        final_poses = tuple(_face_rest_pose(mesh, pose) for pose in raw_final_poses)
        if settled:
            frames = _replace_final_hold_frames(frames, final_poses, fps)
        linear_speeds, angular_speeds = _speeds_for_bodies(p, client, bodies)
        return SimulationResult(
            frames=tuple(frames),
            final_poses=final_poses,
            seed=seed,
            settled=settled,
            settle_time_seconds=settle_time,
            final_linear_speeds=linear_speeds,
            final_angular_speeds=angular_speeds,
            horizontal_travel=_horizontal_travel(frames),
            max_height=_max_height(frames),
            final_contact_vertices=tuple(
                _contact_vertex_count(mesh, pose) for pose in final_poses
            ),
        )
    except MissingDependencyError:
        raise
    except Exception as exc:
        raise SimulationError(f"PyBullet simulation failed: {exc}") from exc
    finally:
        try:
            p.disconnect(client)
        except Exception:
            pass


def _capture_until_settled(
    p: Any, client: int, bodies: list[int], duration_ms: int, fps: int
) -> tuple[list[SimulationFrame], bool, float | None]:
    max_steps = max(1, int(PHYSICS_HZ * duration_ms / 1000))
    capture_interval = max(1, int(PHYSICS_HZ / max(1, fps)))
    quiet_hold_steps = max(1, int(QUIET_HOLD_SECONDS * PHYSICS_HZ))
    post_settle_hold_steps = max(
        capture_interval, int(POST_SETTLE_HOLD_SECONDS * PHYSICS_HZ)
    )
    required_quiet_steps = quiet_hold_steps + post_settle_hold_steps
    frames: list[SimulationFrame] = []
    quiet_steps = 0
    settled_at_step: int | None = None

    for step in range(max_steps):
        p.stepSimulation(physicsClientId=client)
        quiet_steps = (
            quiet_steps + 1
            if all(_body_is_quiet(p, client, body) for body in bodies)
            else 0
        )

        if step % capture_interval == 0:
            frames.append(
                SimulationFrame(
                    time_seconds=step / PHYSICS_HZ,
                    poses=tuple(_pose_for_body(p, client, body) for body in bodies),
                )
            )

        if quiet_steps >= required_quiet_steps:
            settled_at_step = step - required_quiet_steps + 1
            break

    if len(frames) < 2:
        frames.append(
            SimulationFrame(
                time_seconds=max_steps / PHYSICS_HZ,
                poses=tuple(_pose_for_body(p, client, body) for body in bodies),
            )
        )
    final_frame = SimulationFrame(
        time_seconds=frames[-1].time_seconds + capture_interval / PHYSICS_HZ,
        poses=tuple(_pose_for_body(p, client, body) for body in bodies),
    )
    if final_frame.poses != frames[-1].poses:
        frames.append(final_frame)
    settle_time = None if settled_at_step is None else settled_at_step / PHYSICS_HZ
    return frames, settled_at_step is not None, settle_time


def _body_is_quiet(p: Any, client: int, body: int) -> bool:
    linear, angular = p.getBaseVelocity(body, physicsClientId=client)
    return (
        np.linalg.norm(linear) < QUIET_LINEAR_SPEED
        and np.linalg.norm(angular) < QUIET_ANGULAR_SPEED
    )


def _pose_for_body(p: Any, client: int, body: int) -> BodyPose:
    position, orientation = p.getBasePositionAndOrientation(
        body, physicsClientId=client
    )
    return BodyPose(
        position=tuple(float(value) for value in position),
        orientation=tuple(float(value) for value in orientation),
    )


def _speeds_for_bodies(
    p: Any, client: int, bodies: list[int]
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    linear_speeds = []
    angular_speeds = []
    for body in bodies:
        linear, angular = p.getBaseVelocity(body, physicsClientId=client)
        linear_speeds.append(float(np.linalg.norm(linear)))
        angular_speeds.append(float(np.linalg.norm(angular)))
    return tuple(linear_speeds), tuple(angular_speeds)


def _horizontal_travel(frames: list[SimulationFrame]) -> float:
    if not frames or not frames[0].poses:
        return 0.0
    max_travel = 0.0
    body_count = len(frames[0].poses)
    for body_index in range(body_count):
        start = np.asarray(frames[0].poses[body_index].position[:2], dtype=float)
        for frame in frames:
            current = np.asarray(frame.poses[body_index].position[:2], dtype=float)
            max_travel = max(max_travel, float(np.linalg.norm(current - start)))
    return max_travel


def _max_height(frames: list[SimulationFrame]) -> float:
    if not frames:
        return 0.0
    return max(float(pose.position[2]) for frame in frames for pose in frame.poses)


def _face_rest_pose(mesh: MeshData, pose: BodyPose) -> BodyPose:
    rotation = quaternion_to_matrix(pose.orientation)
    world_normals = mesh.result_normals @ rotation.T
    bottom_index = int(np.argmin(world_normals[:, 2]))
    correction = _rotation_between(
        world_normals[bottom_index], np.array([0.0, 0.0, -1.0])
    )
    corrected_rotation = correction @ rotation
    position = np.asarray(pose.position, dtype=float)
    points = mesh.vertices @ corrected_rotation.T + position
    position[2] += TABLE_TOP_Z - float(points[:, 2].min()) + 0.001
    return BodyPose(
        position=tuple(float(value) for value in position),
        orientation=_matrix_to_quaternion(corrected_rotation),
    )


def _replace_final_hold_frames(
    frames: list[SimulationFrame], final_poses: tuple[BodyPose, ...], fps: int
) -> list[SimulationFrame]:
    if not frames:
        return frames
    hold_frames = max(2, int(round(POST_SETTLE_HOLD_SECONDS * max(1, fps))))
    start = max(0, len(frames) - hold_frames)
    return [
        frame if index < start else SimulationFrame(frame.time_seconds, final_poses)
        for index, frame in enumerate(frames)
    ]


def _contact_vertex_count(mesh: MeshData, pose: BodyPose) -> int:
    points = mesh.vertices @ quaternion_to_matrix(pose.orientation).T + np.asarray(
        pose.position
    )
    min_z = float(points[:, 2].min())
    return int(np.sum(points[:, 2] <= min_z + 0.002))


def _rotation_between(source: np.ndarray, target: np.ndarray) -> np.ndarray:
    source = source / np.linalg.norm(source)
    target = target / np.linalg.norm(target)
    cross = np.cross(source, target)
    dot = float(np.clip(np.dot(source, target), -1.0, 1.0))
    if dot > 0.999999:
        return np.eye(3)
    if dot < -0.999999:
        axis = np.cross(source, np.array([1.0, 0.0, 0.0]))
        if np.linalg.norm(axis) < 1e-6:
            axis = np.cross(source, np.array([0.0, 1.0, 0.0]))
        axis = axis / np.linalg.norm(axis)
        return _axis_angle_matrix(axis, math.pi)
    skew = np.array(
        [
            [0.0, -cross[2], cross[1]],
            [cross[2], 0.0, -cross[0]],
            [-cross[1], cross[0], 0.0],
        ]
    )
    return np.eye(3) + skew + skew @ skew * (1.0 / (1.0 + dot))


def _axis_angle_matrix(axis: np.ndarray, angle: float) -> np.ndarray:
    x, y, z = axis
    c = math.cos(angle)
    s = math.sin(angle)
    one_c = 1 - c
    return np.array(
        [
            [c + x * x * one_c, x * y * one_c - z * s, x * z * one_c + y * s],
            [y * x * one_c + z * s, c + y * y * one_c, y * z * one_c - x * s],
            [z * x * one_c - y * s, z * y * one_c + x * s, c + z * z * one_c],
        ],
        dtype=float,
    )


def _matrix_to_quaternion(matrix: np.ndarray) -> tuple[float, float, float, float]:
    trace = float(np.trace(matrix))
    if trace > 0:
        s = math.sqrt(trace + 1.0) * 2
        w = 0.25 * s
        x = (matrix[2, 1] - matrix[1, 2]) / s
        y = (matrix[0, 2] - matrix[2, 0]) / s
        z = (matrix[1, 0] - matrix[0, 1]) / s
    else:
        index = int(np.argmax(np.diag(matrix)))
        if index == 0:
            s = math.sqrt(1.0 + matrix[0, 0] - matrix[1, 1] - matrix[2, 2]) * 2
            w = (matrix[2, 1] - matrix[1, 2]) / s
            x = 0.25 * s
            y = (matrix[0, 1] + matrix[1, 0]) / s
            z = (matrix[0, 2] + matrix[2, 0]) / s
        elif index == 1:
            s = math.sqrt(1.0 + matrix[1, 1] - matrix[0, 0] - matrix[2, 2]) * 2
            w = (matrix[0, 2] - matrix[2, 0]) / s
            x = (matrix[0, 1] + matrix[1, 0]) / s
            y = 0.25 * s
            z = (matrix[1, 2] + matrix[2, 1]) / s
        else:
            s = math.sqrt(1.0 + matrix[2, 2] - matrix[0, 0] - matrix[1, 1]) * 2
            w = (matrix[1, 0] - matrix[0, 1]) / s
            x = (matrix[0, 2] + matrix[2, 0]) / s
            y = (matrix[1, 2] + matrix[2, 1]) / s
            z = 0.25 * s
    norm = math.sqrt(x * x + y * y + z * z + w * w)
    return (float(x / norm), float(y / norm), float(z / norm), float(w / norm))


def _load_pybullet() -> Any:
    try:
        import pybullet as p  # type: ignore
    except Exception as exc:
        raise MissingDependencyError(
            "pybullet is required for physical dice simulation. "
            "Install plugin requirements with: pip install -r requirements.txt"
        ) from exc
    return p
