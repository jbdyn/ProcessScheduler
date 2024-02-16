# Copyright (c) 2020-2021 Thomas Paviot (tpaviot@gmail.com)
#
# This file is part of ProcessScheduler.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.


import processscheduler as ps

import pytest


def test_resource_work_load_basic() -> None:
    pb = ps.SchedulingProblem(name="ResourceWorkLoadBasic", horizon=12)
    task_1 = ps.FixedDurationTask(name="task1", duration=8)

    worker_1 = ps.Worker(name="Worker1")
    task_1.add_required_resource(worker_1)

    ps.WorkLoad(resource=worker_1, dict_time_intervals_and_bound={(0, 6): 2})

    solver = ps.SchedulingSolver(problem=pb)
    solution = solver.solve()
    assert solution
    # the only possible solution is that the task is scheduled form 4 to 12
    assert solution.tasks[task_1.name].start == 4
    assert solution.tasks[task_1.name].end == 12


def test_resource_work_load_eq() -> None:
    pb = ps.SchedulingProblem(name="ResourceWorkLoadEq", horizon=12)
    task_1 = ps.FixedDurationTask(name="task1", duration=7)

    worker_1 = ps.Worker(name="Worker1")
    task_1.add_required_resource(worker_1)

    ps.WorkLoad(
        resource=worker_1, dict_time_intervals_and_bound={(0, 6): 3}, kind="exact"
    )
    solver = ps.SchedulingSolver(problem=pb)
    solution = solver.solve()
    assert solution
    # the only possible solution is that the task is scheduled form 3 to 9
    assert solution.tasks[task_1.name].start == 3
    assert solution.tasks[task_1.name].end == 10


def test_resource_work_load_min() -> None:
    pb = ps.SchedulingProblem(name="ResourceWorkLoadMin", horizon=20)
    task_1 = ps.FixedDurationTask(name="task1", duration=7)

    worker_1 = ps.Worker(name="Worker1")
    task_1.add_required_resource(worker_1)

    ps.WorkLoad(
        resource=worker_1, dict_time_intervals_and_bound={(6, 8): 2}, kind="min"
    )

    solver = ps.SchedulingSolver(problem=pb)
    solution = solver.solve()

    assert solution
    # the only possible solution is that the task is scheduled form 3 to 9
    assert solution.tasks[task_1.name].start <= 6
    assert solution.tasks[task_1.name].end >= 8


def test_resource_work_load_3() -> None:
    # same problem, but we force two tasks to be scheduled at start and end
    # of the planning
    pb = ps.SchedulingProblem(name="ResourceWorkLoadUnavailability", horizon=12)
    task_1 = ps.FixedDurationTask(name="task1", duration=4)
    task_2 = ps.FixedDurationTask(name="task2", duration=4)
    worker_1 = ps.Worker(name="Worker1")
    task_1.add_required_resource(worker_1)
    task_2.add_required_resource(worker_1)

    ps.WorkLoad(resource=worker_1, dict_time_intervals_and_bound={(4, 8): 0})

    solver = ps.SchedulingSolver(problem=pb)
    solution = solver.solve()
    assert solution
    # there should be one task from 0 to 4 and one task from 8 to 12.
    assert (
        solution.tasks[task_1.name].start == 0 or solution.tasks[task_2.name].start == 0
    )

    assert (
        solution.tasks[task_1.name].start == 8 or solution.tasks[task_2.name].start == 8
    )


def test_resource_work_load_exception() -> None:
    ps.SchedulingProblem(name="ResourceWorkLoadException", horizon=12)

    worker_1 = ps.Worker(name="Worker1")

    with pytest.raises(ValueError):
        ps.WorkLoad(
            resource=worker_1, dict_time_intervals_and_bound={(0, 6): 2}, kind="foo"
        )


def test_selectworker_work_load_1() -> None:
    pb = ps.SchedulingProblem(name="SelectWorkerWorkLoad1", horizon=12)

    worker_1 = ps.Worker(name="Worker1")
    worker_2 = ps.Worker(name="Worker2")

    task1 = ps.FixedDurationTask(name="Task1", duration=10)

    task1.add_required_resource(
        ps.SelectWorkers(
            list_of_workers=[worker_1, worker_2], nb_workers_to_select=1, kind="min"
        )
    )
    # the workload on worker_1 forces 0 between 4 and 8
    # then the worker_1 can not be assigned
    ps.WorkLoad(resource=worker_1, dict_time_intervals_and_bound={(4, 8): 0})

    solver = ps.SchedulingSolver(problem=pb)
    solution = solver.solve()
    print(solution)
    assert solution
    assert solution.tasks[task1.name].assigned_resources == [worker_2.name]


def test_multiple_workers_work_load_1() -> None:
    pb = ps.SchedulingProblem(name="MultipleWorkersWorkLoad1", horizon=12)

    worker_1 = ps.Worker(name="Worker1")
    worker_2 = ps.Worker(name="Worker2")

    task1 = ps.FixedDurationTask(name="Task1", duration=10)
    task1.add_required_resources([worker_1, worker_2])

    ps.WorkLoad(resource=worker_1, dict_time_intervals_and_bound={(0, 4): 2})
    ps.WorkLoad(
        resource=worker_2, dict_time_intervals_and_bound={(2, 6): 2}, kind="min"
    )

    solver = ps.SchedulingSolver(problem=pb)
    solution = solver.solve()
    assert solution
    assert solution.tasks[task1.name].start == 2


def test_multiple_workers_work_load_2() -> None:
    ### the same as above but changing 'min' to 'exact', there's no solution
    pb = ps.SchedulingProblem(name="MultipleWorkersWorkLoad2", horizon=12)

    worker_1 = ps.Worker(name="Worker1")
    worker_2 = ps.Worker(name="Worker2")

    task1 = ps.FixedDurationTask(name="Task1", duration=10)
    task1.add_required_resources([worker_1, worker_2])

    ps.WorkLoad(resource=worker_1, dict_time_intervals_and_bound={(0, 4): 2})
    ps.WorkLoad(
        resource=worker_2, dict_time_intervals_and_bound={(2, 6): 2}, kind="exact"
    )

    solver = ps.SchedulingSolver(problem=pb)
    solution = solver.solve()
    assert not solution


# WorkLoad for a cumulative resource
def test_cumulative_resource_work_load_1() -> None:
    # same problem, but we force two tasks to be scheduled at start and end
    # of the planning
    pb = ps.SchedulingProblem(
        name="CumulativeResourceWorkLoadUnavailability", horizon=12
    )
    # both tasks 1 can be run in parallel
    task_1 = ps.FixedDurationTask(name="task1", duration=4)
    task_2 = ps.FixedDurationTask(name="task2", duration=4)
    worker_1 = ps.CumulativeWorker(name="Worker1", size=2)
    task_1.add_required_resource(worker_1)
    task_2.add_required_resource(worker_1)

    ps.WorkLoad(resource=worker_1, dict_time_intervals_and_bound={(3, 8): 0})

    solver = ps.SchedulingSolver(problem=pb)
    solution = solver.solve()
    assert solution
    # both tasks should start at 8.
    assert (
        solution.tasks[task_1.name].start == 8
        and solution.tasks[task_2.name].start == 8
    )


def test_resource_workload_raise_issue() -> None:
    ps.SchedulingProblem(name="ResourceWorkloadRaiseIssue", horizon=10)
    worker_1 = ps.Worker(name="Worker1")
    with pytest.raises(AssertionError):
        ps.WorkLoad(resource=worker_1, dict_time_intervals_and_bound={(3, 8): 0})
