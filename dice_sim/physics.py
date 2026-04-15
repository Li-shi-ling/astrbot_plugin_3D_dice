from __future__ import annotations

import math
import random
from typing import Any

import numpy as np

from .errors import MissingDependencyError, SimulationError
from .types import BodyPose, MeshData, SimulationFrame, SimulationResult

PHYSICS_HZ = 240


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

        plane = p.createCollisionShape(p.GEOM_PLANE, physicsClientId=client)
        plane_body = p.createMultiBody(
            baseMass=0,
            baseCollisionShapeIndex=plane,
            basePosition=[0, 0, 0],
            physicsClientId=client,
        )
        p.changeDynamics(
            plane_body,
            -1,
            lateralFriction=0.95,
            restitution=0.35,
            physicsClientId=client,
        )

        collision = p.createCollisionShape(
            shapeType=p.GEOM_MESH,
            vertices=mesh.vertices.tolist(),
            indices=mesh.faces.reshape(-1).astype(int).tolist(),
            physicsClientId=client,
        )
        visual = p.createVisualShape(
            shapeType=p.GEOM_MESH,
            vertices=mesh.vertices.tolist(),
            indices=mesh.faces.reshape(-1).astype(int).tolist(),
            rgbaColor=[0.82, 0.14, 0.12, 1.0],
            physicsClientId=client,
        )

        spacing = 1.8
        start_x = -spacing * (count - 1) / 2
        for idx in range(count):
            position = [
                start_x + idx * spacing + rng.uniform(-0.18, 0.18),
                rng.uniform(-0.25, 0.25),
                2.2 + idx * 0.18,
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
                lateralFriction=0.82,
                restitution=0.42,
                rollingFriction=0.05,
                spinningFriction=0.04,
                linearDamping=0.06,
                angularDamping=0.06,
                physicsClientId=client,
            )
            p.resetBaseVelocity(
                body,
                linearVelocity=[
                    rng.uniform(-1.4, 1.4),
                    rng.uniform(-1.4, 1.4),
                    rng.uniform(0.7, 2.2),
                ],
                angularVelocity=[
                    rng.uniform(-18.0, 18.0),
                    rng.uniform(-18.0, 18.0),
                    rng.uniform(-18.0, 18.0),
                ],
                physicsClientId=client,
            )
            bodies.append(body)

        frames = _capture_frames(p, client, bodies, duration_ms, fps)
        _settle(p, client, bodies)
        final_poses = tuple(_pose_for_body(p, client, body) for body in bodies)
        return SimulationResult(frames=tuple(frames), final_poses=final_poses, seed=seed)
    except MissingDependencyError:
        raise
    except Exception as exc:
        raise SimulationError(f"PyBullet simulation failed: {exc}") from exc
    finally:
        try:
            p.disconnect(client)
        except Exception:
            pass


def _capture_frames(
    p: Any, client: int, bodies: list[int], duration_ms: int, fps: int
) -> list[SimulationFrame]:
    total_steps = max(1, int(PHYSICS_HZ * duration_ms / 1000))
    capture_interval = max(1, int(PHYSICS_HZ / max(1, fps)))
    frames: list[SimulationFrame] = []
    for step in range(total_steps):
        p.stepSimulation(physicsClientId=client)
        if step % capture_interval == 0:
            frames.append(
                SimulationFrame(
                    time_seconds=step / PHYSICS_HZ,
                    poses=tuple(_pose_for_body(p, client, body) for body in bodies),
                )
            )
    if len(frames) < 2:
        frames.append(
            SimulationFrame(
                time_seconds=total_steps / PHYSICS_HZ,
                poses=tuple(_pose_for_body(p, client, body) for body in bodies),
            )
        )
    return frames


def _settle(p: Any, client: int, bodies: list[int]) -> None:
    for _ in range(PHYSICS_HZ):
        p.stepSimulation(physicsClientId=client)
        if all(_body_is_quiet(p, client, body) for body in bodies):
            return


def _body_is_quiet(p: Any, client: int, body: int) -> bool:
    linear, angular = p.getBaseVelocity(body, physicsClientId=client)
    return np.linalg.norm(linear) < 0.08 and np.linalg.norm(angular) < 0.12


def _pose_for_body(p: Any, client: int, body: int) -> BodyPose:
    position, orientation = p.getBasePositionAndOrientation(body, physicsClientId=client)
    return BodyPose(
        position=tuple(float(value) for value in position),
        orientation=tuple(float(value) for value in orientation),
    )


def _load_pybullet() -> Any:
    try:
        import pybullet as p  # type: ignore
    except Exception as exc:
        raise MissingDependencyError(
            "pybullet is required for physical dice simulation. "
            "Install plugin requirements with: pip install -r requirements.txt"
        ) from exc
    return p
