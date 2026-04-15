from __future__ import annotations

import math
import random
from typing import Any

import numpy as np

from .errors import MissingDependencyError, SimulationError
from .result import quaternion_to_matrix
from .types import BodyPose, MeshData, SimulationFrame, SimulationResult

PHYSICS_HZ = 240
QUIET_LINEAR_SPEED = 0.12
QUIET_ANGULAR_SPEED = 0.25
QUIET_HOLD_SECONDS = 0.25
POST_SETTLE_HOLD_SECONDS = 0.35
FINAL_FACE_TRANSITION_SECONDS = 1.20
TABLE_HALF_EXTENTS = [24.0, 16.0, 0.08]
TABLE_TOP_Z = 0.0
THROW_START_X = -5.7
THROW_START_Y = -2.35
THROW_START_Z = 2.55
MULTI_DICE_COLUMN_GAP = 2.45
MULTI_DICE_ROW_GAP = 2.55
D6_TUMBLE_SPEED_RANGE = (13.0, 18.0)


def simulate_roll(
    mesh: MeshData,
    count: int,
    seed: int,
    duration_ms: int,
    fps: int,
    final_hold_ms: int = 3000,
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
            lateralFriction=1.10,
            restitution=0.14,
            rollingFriction=0.08,
            spinningFriction=0.06,
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

        for idx in range(count):
            position = _initial_position(count, idx, rng)
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
            dynamics = _body_dynamics(mesh, count)
            p.changeDynamics(
                body,
                -1,
                lateralFriction=dynamics["lateral_friction"],
                restitution=dynamics["restitution"],
                rollingFriction=dynamics["rolling_friction"],
                spinningFriction=dynamics["spinning_friction"],
                linearDamping=dynamics["linear_damping"],
                angularDamping=dynamics["angular_damping"],
                physicsClientId=client,
            )
            target = _throw_target(count, idx, rng)
            linear_velocity = _initial_linear_velocity(
                mesh, count, position, target, rng
            )
            p.resetBaseVelocity(
                body,
                linearVelocity=linear_velocity,
                angularVelocity=_initial_angular_velocity(mesh, linear_velocity, rng),
                physicsClientId=client,
            )
            bodies.append(body)

        (
            frames,
            settled,
            settle_time,
            body_contact_count,
            body_contact_steps,
        ) = _capture_until_settled(p, client, bodies, duration_ms, fps)
        raw_final_poses = tuple(_pose_for_body(p, client, body) for body in bodies)
        final_poses = tuple(_face_rest_pose(mesh, pose) for pose in raw_final_poses)
        result_label_start = settle_time
        if settled:
            frames, result_label_start = _append_final_hold_frames(
                frames,
                final_poses,
                fps,
                settle_time,
                max(0.0, final_hold_ms / 1000.0),
            )
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
            inter_body_contact_count=body_contact_count,
            inter_body_contact_steps=body_contact_steps,
            result_label_start_seconds=result_label_start,
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


def _initial_position(count: int, idx: int, rng: random.Random) -> list[float]:
    if count <= 1:
        return [
            THROW_START_X + rng.uniform(-0.12, 0.12),
            THROW_START_Y + rng.uniform(-0.16, 0.16),
            THROW_START_Z + rng.uniform(-0.05, 0.08),
        ]

    columns = 2 if count > 3 else 1
    rows = math.ceil(count / columns)
    column = idx % columns
    row = idx // columns
    return [
        THROW_START_X + column * MULTI_DICE_COLUMN_GAP + rng.uniform(-0.04, 0.04),
        THROW_START_Y
        + (row - (rows - 1) / 2) * MULTI_DICE_ROW_GAP
        + rng.uniform(-0.07, 0.07),
        THROW_START_Z + row * 0.16 + column * 0.10 + rng.uniform(-0.03, 0.06),
    ]


def _throw_target(count: int, idx: int, rng: random.Random) -> list[float]:
    if count <= 1:
        return [1.2 + rng.uniform(-0.35, 0.35), 0.0 + rng.uniform(-0.45, 0.45)]
    lane_bias = (idx - (count - 1) / 2) * 0.10
    return [
        0.55 + rng.uniform(-0.45, 0.45),
        lane_bias + rng.uniform(-0.55, 0.55),
    ]


def _body_dynamics(mesh: MeshData, count: int) -> dict[str, float]:
    if mesh.dice_type == "D6":
        if count > 1:
            return {
                "lateral_friction": 1.12,
                "restitution": 0.13,
                "rolling_friction": 0.10,
                "spinning_friction": 0.075,
                "linear_damping": 0.010,
                "angular_damping": 0.012,
            }
        return {
            "lateral_friction": 1.00,
            "restitution": 0.18,
            "rolling_friction": 0.045,
            "spinning_friction": 0.032,
            "linear_damping": 0.006,
            "angular_damping": 0.004,
        }
    if mesh.dice_type == "D8":
        if count > 1:
            return {
                "lateral_friction": 1.18,
                "restitution": 0.12,
                "rolling_friction": 0.16,
                "spinning_friction": 0.13,
                "linear_damping": 0.013,
                "angular_damping": 0.018,
            }
        return {
            "lateral_friction": 1.10,
            "restitution": 0.14,
            "rolling_friction": 0.12,
            "spinning_friction": 0.095,
            "linear_damping": 0.012,
            "angular_damping": 0.014,
        }
    return {
        "lateral_friction": 1.08,
        "restitution": 0.14,
        "rolling_friction": 0.11,
        "spinning_friction": 0.085,
        "linear_damping": 0.012,
        "angular_damping": 0.014,
    }


def _initial_linear_velocity(
    mesh: MeshData,
    count: int,
    position: list[float],
    target: list[float],
    rng: random.Random,
) -> list[float]:
    travel_seconds = rng.uniform(1.35, 1.70) if count > 1 else rng.uniform(1.05, 1.32)
    velocity_x = (target[0] - position[0]) / travel_seconds
    velocity_y = (target[1] - position[1]) / travel_seconds
    if mesh.dice_type == "D6":
        vertical_speed = rng.uniform(3.2, 4.0) if count > 1 else rng.uniform(4.0, 5.0)
        return [
            velocity_x + rng.uniform(-0.18, 0.18),
            velocity_y + rng.uniform(-0.18, 0.18),
            vertical_speed,
        ]
    vertical_speed = rng.uniform(2.8, 3.6) if count > 1 else rng.uniform(3.0, 4.2)
    return [
        velocity_x + rng.uniform(-0.22, 0.22),
        velocity_y + rng.uniform(-0.22, 0.22),
        vertical_speed,
    ]


def _initial_angular_velocity(
    mesh: MeshData, linear_velocity: list[float], rng: random.Random
) -> list[float]:
    if mesh.dice_type != "D6":
        return [
            rng.uniform(-34.0, 34.0),
            rng.uniform(-34.0, 34.0),
            rng.uniform(-34.0, 34.0),
        ]

    travel = np.array([linear_velocity[0], linear_velocity[1], 0.0], dtype=float)
    travel_norm = float(np.linalg.norm(travel))
    if travel_norm < 1e-6:
        travel = np.array([1.0, 0.0, 0.0], dtype=float)
    else:
        travel /= travel_norm
    roll_axis = np.cross(np.array([0.0, 0.0, 1.0], dtype=float), travel)
    roll_axis_norm = float(np.linalg.norm(roll_axis))
    if roll_axis_norm < 1e-6:
        roll_axis = np.array([0.0, 1.0, 0.0], dtype=float)
    else:
        roll_axis /= roll_axis_norm

    tumble = roll_axis * rng.choice((-1.0, 1.0)) * rng.uniform(*D6_TUMBLE_SPEED_RANGE)
    side_roll = travel * rng.uniform(-3.5, 3.5)
    yaw = np.array([0.0, 0.0, rng.uniform(-2.5, 2.5)], dtype=float)
    angular = tumble + side_roll + yaw
    return [float(component) for component in angular]


def _capture_until_settled(
    p: Any, client: int, bodies: list[int], duration_ms: int, fps: int
) -> tuple[list[SimulationFrame], bool, float | None, int, int]:
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
    body_contact_count = 0
    body_contact_steps = 0

    for step in range(max_steps):
        p.stepSimulation(physicsClientId=client)
        contact_pairs = _inter_body_contact_pairs(p, client, bodies)
        if contact_pairs:
            body_contact_count += len(contact_pairs)
            body_contact_steps += 1
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
    return (
        frames,
        settled_at_step is not None,
        settle_time,
        body_contact_count,
        body_contact_steps,
    )


def _inter_body_contact_pairs(
    p: Any, client: int, bodies: list[int]
) -> set[tuple[int, int]]:
    if len(bodies) < 2:
        return set()
    body_ids = set(bodies)
    pairs: set[tuple[int, int]] = set()
    for contact in p.getContactPoints(physicsClientId=client):
        body_a = int(contact[1])
        body_b = int(contact[2])
        if body_a in body_ids and body_b in body_ids and body_a != body_b:
            pairs.add(tuple(sorted((body_a, body_b))))
    return pairs


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


def _append_final_hold_frames(
    frames: list[SimulationFrame],
    final_poses: tuple[BodyPose, ...],
    fps: int,
    settle_time: float | None,
    final_hold_seconds: float,
) -> tuple[list[SimulationFrame], float | None]:
    if not frames:
        return frames, settle_time
    frame_rate = max(1, fps)
    start = len(frames) - 1
    if settle_time is not None:
        for index, frame in enumerate(frames):
            if frame.time_seconds >= settle_time:
                start = index
                break

    output = frames[: start + 1]
    source_frame = output[-1]
    transition_frames = max(
        1, int(round(FINAL_FACE_TRANSITION_SECONDS * frame_rate))
    )
    hold_frames = max(1, int(round(final_hold_seconds * frame_rate)))
    frame_interval = 1.0 / frame_rate

    for step in range(1, transition_frames + 1):
        amount = _smoothstep(step / transition_frames)
        poses = tuple(
            _interpolate_pose(source, target, amount)
            for source, target in zip(source_frame.poses, final_poses)
        )
        output.append(
            SimulationFrame(
                source_frame.time_seconds + step * frame_interval,
                poses,
            )
        )

    hold_start = output[-1].time_seconds
    for step in range(1, hold_frames + 1):
        output.append(
            SimulationFrame(
                hold_start + step * frame_interval,
                final_poses,
            )
        )

    return output, hold_start


def _interpolate_pose(source: BodyPose, target: BodyPose, amount: float) -> BodyPose:
    source_position = np.asarray(source.position, dtype=float)
    target_position = np.asarray(target.position, dtype=float)
    position = source_position * (1.0 - amount) + target_position * amount
    return BodyPose(
        position=tuple(float(value) for value in position),
        orientation=_slerp_quaternion(source.orientation, target.orientation, amount),
    )


def _slerp_quaternion(
    source: tuple[float, float, float, float],
    target: tuple[float, float, float, float],
    amount: float,
) -> tuple[float, float, float, float]:
    start = np.asarray(source, dtype=float)
    end = np.asarray(target, dtype=float)
    start = start / np.linalg.norm(start)
    end = end / np.linalg.norm(end)
    dot = float(np.dot(start, end))
    if dot < 0.0:
        end = -end
        dot = -dot
    if dot > 0.9995:
        value = start + amount * (end - start)
        value /= np.linalg.norm(value)
        return tuple(float(component) for component in value)

    theta_0 = math.acos(float(np.clip(dot, -1.0, 1.0)))
    theta = theta_0 * amount
    sin_theta = math.sin(theta)
    sin_theta_0 = math.sin(theta_0)
    scale_start = math.cos(theta) - dot * sin_theta / sin_theta_0
    scale_end = sin_theta / sin_theta_0
    value = scale_start * start + scale_end * end
    return tuple(float(component) for component in value)


def _smoothstep(amount: float) -> float:
    clamped = float(np.clip(amount, 0.0, 1.0))
    return clamped * clamped * (3.0 - 2.0 * clamped)


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
