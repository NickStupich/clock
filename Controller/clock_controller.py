import asyncio
import datetime
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "Simulator"))

import ArduinoInterface  # noqa: E402
import Constants  # noqa: E402
import DrawClock  # noqa: E402
from DisplayAlgorithms import (  # noqa: E402
    BacklashDisplayAlgorithm,
    CalibrationDisplayAlgorithm,
    DebugAlgorithm,
    OffDisplayAlgorithm,
    SimpleTimeAlgorithm,
    TestMotorsAlgorithm,
    TextDisplayAlgorithm,
    TimeDisplayAlgorithm,
    TimeDisplayAlgorithm2,
    TimeDisplayAlgorithm3,
    TimeDisplayAlgorithm4,
    TimeDisplayAlgorithm5,
)

SHAPE = DrawClock.clock_positions_base.shape
PHYSICS_PERIOD = 1 / 30
TARGET_PERIOD = 1.0
TRIGGER_OFFSET = 0.5  # hands are triggered half a period after targets are sent

OVERNIGHT_MODES = ["Normal", "Minimal", "Off"]
OVERNIGHT_HOURS = {22, 23, 0, 1, 2, 3, 4, 5, 6}
NO_OVERNIGHT_ALGOS = {"Off", "Calibration", "MotorTest"}


class ClockController:
    """Owns all hand state. Mutated only on the event loop; I2C calls run on a single worker thread."""

    def __init__(self, publish_frame, publish_event, commit):
        self._publish_frame = publish_frame
        self._publish_event = publish_event
        self.commit = commit

        self.target = np.zeros(SHAPE)
        self.actual = np.zeros(SHAPE)
        self.velocity = np.zeros(SHAPE)
        self.new_moves = np.zeros(SHAPE, dtype=int)
        self.in_progress = np.zeros(SHAPE, dtype=int)
        self.speeds = np.full(SHAPE, Constants.BASE_VELOCITY, dtype=float)
        self.calibration = np.zeros(SHAPE)
        self.backlash = np.zeros(SHAPE)

        self.arduino = ArduinoInterface.ArduinoInterface()
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="i2c")
        self._moves_lock = asyncio.Lock()
        self._tasks = []
        self._last_frame = b""

        self.algorithms = {
            "Off": OffDisplayAlgorithm.OffDisplayAlgorithm(),
            "Time": TimeDisplayAlgorithm.TimeDisplayAlgorithm(),
            "Time2": TimeDisplayAlgorithm2.TimeDisplayAlgorithm2(),
            "Time3": TimeDisplayAlgorithm3.TimeDisplayAlgorithm3(),
            "Time4": TimeDisplayAlgorithm4.TimeDisplayAlgorithm4(),
            "Time5": TimeDisplayAlgorithm5.TimeDisplayAlgorithm5(),
            "Minimal": SimpleTimeAlgorithm.SimpleTimeAlgorithm(),
            "Text": TextDisplayAlgorithm.TextDisplayAlgorithm(),
            "MotorTest": TestMotorsAlgorithm.TestMotorsAlgorithm(),
            "Calibration": CalibrationDisplayAlgorithm.CalibrationDisplayAlgorithm(),
            "Backlash": BacklashDisplayAlgorithm.BacklashDisplayAlgorithm(),
            "Debug": DebugAlgorithm.DebugAlgorithm(),
        }
        self.algorithm_name = "Off"
        self.overnight_mode = "Minimal"
        self.log = ""

    def start(self):
        self._tasks = [
            asyncio.create_task(self._physics_loop()),
            asyncio.create_task(self._target_loop()),
        ]

    async def stop(self):
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._executor.shutdown(wait=False)

    def frame(self):
        return self.actual.astype("<f4").tobytes()

    def snapshot(self):
        return {
            "type": "state",
            "config": {
                "rows": DrawClock.n_rows,
                "cols": DrawClock.n_cols,
                "spacing": DrawClock.distance_between_clocks,
                "handLength": DrawClock.hand_length,
                "handWidth": DrawClock.hand_width,
                "clockRadius": DrawClock.clock_radius,
                "width": DrawClock.plot_width,
                "height": DrawClock.plot_height,
                "padX": DrawClock.horizontal_border_padding,
                "padY": DrawClock.vertical_border_padding,
                "backHandColor": DrawClock.back_hand_color,
                "frontHandColor": DrawClock.front_hand_color,
                "backgroundColor": DrawClock.background_color,
                "recessLineColor": DrawClock.individual_recess_line_color,
                "recessFillColor": DrawClock.individual_recess_fill_color,
            },
            "algorithms": list(self.algorithms),
            "algorithm": self.algorithm_name,
            "overnightModes": OVERNIGHT_MODES,
            "overnightMode": self.overnight_mode,
            "interface": self.arduino.name,
            "commit": self.commit,
            "log": self.log,
        }

    def enable_algo(self, name):
        if name not in self.algorithms:
            return False
        self.algorithm_name = name
        self.speeds[:] = Constants.BASE_VELOCITY
        self.algorithms[name].select()
        self._publish_event({"type": "algorithm", "value": name})
        return True

    def set_overnight_mode(self, mode):
        if mode not in OVERNIGHT_MODES:
            return False
        self.overnight_mode = mode
        self._publish_event({"type": "overnightMode", "value": mode})
        return True

    def set_log(self, text):
        self.log = text
        self._publish_event({"type": "log", "value": text})

    async def set_calibration(self, new_values):
        if self.algorithm_name == "Calibration":
            self.calibration = new_values
            setter, delta = self.arduino.setCalibrationOffsets, 360
        elif self.algorithm_name == "Backlash":
            self.backlash = new_values
            setter, delta = self.arduino.setBacklashOffsets, -360
        else:
            return False

        async with self._moves_lock:
            await self._io(setter, new_values)
            self.target += delta
            all_moves = np.ones_like(self.new_moves)
            await self._io(self.arduino.transmitTargetPositions, self.target.copy(), all_moves, self.speeds.copy())
            await self._io(self.arduino.triggerHandMoves)
            self.in_progress[:] = 1
        return True

    def _io(self, fn, *args):
        return asyncio.get_running_loop().run_in_executor(self._executor, fn, *args)

    def _effective_algorithm(self, hour):
        overnight = hour in OVERNIGHT_HOURS and self.algorithm_name not in NO_OVERNIGHT_ALGOS
        if overnight and self.overnight_mode == "Minimal":
            return self.algorithms["Minimal"]
        if overnight and self.overnight_mode == "Off":
            return self.algorithms["Off"]
        return self.algorithms[self.algorithm_name]

    async def _target_loop(self):
        await asyncio.sleep(1 - datetime.datetime.now().microsecond / 1e6)  # start on a wall-clock second
        tick = time.monotonic()
        while True:
            try:
                await self._run_tick(tick)
            except asyncio.CancelledError:
                raise
            except Exception:
                traceback.print_exc()
            tick += TARGET_PERIOD
            delay = tick - time.monotonic()
            if delay < 0:
                tick, delay = time.monotonic(), 0
            await asyncio.sleep(delay)

    async def _run_tick(self, tick):
        now = datetime.datetime.now()
        async with self._moves_lock:
            self.new_moves[:] = 0
            self._effective_algorithm(now.hour).updateHandPositions(
                now.hour, now.minute, now.second, self.target, self.new_moves, self.speeds)

            if not self.new_moves.any():
                return

            moves = self.new_moves.copy()
            await self._io(self.arduino.transmitTargetPositions, self.target.copy(), moves, self.speeds.copy())
            delay = tick + TRIGGER_OFFSET - time.monotonic()
            if delay > 0:
                await asyncio.sleep(delay)
            await self._io(self.arduino.triggerHandMoves)
            self.in_progress[moves != 0] = 1

    async def _physics_loop(self):
        last = time.monotonic()
        while True:
            await asyncio.sleep(PHYSICS_PERIOD)
            now = time.monotonic()
            self._step(now - last)
            last = now

            frame = self.frame()
            if frame != self._last_frame:
                self._last_frame = frame
                self._publish_frame(frame)

    def _step(self, dt):
        moving = self.in_progress.astype(bool)
        if not moving.any():
            return

        distance = self.target - self.actual
        self.velocity[moving] += (np.sign(distance) * Constants.ACCELERATION * dt)[moving]
        np.clip(self.velocity, -self.speeds, self.speeds, out=self.velocity)

        new_actual = self.actual + self.velocity * dt
        stopped = moving & ((self.target - new_actual) * distance <= 0)

        self.actual[moving] = new_actual[moving]
        self.target[stopped] %= 360
        self.actual[stopped] = self.target[stopped]
        self.velocity[stopped] = 0
        self.in_progress[stopped] = 0
