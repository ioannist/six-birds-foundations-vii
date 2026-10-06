from foundations_vi_lab.g03_currency.binary_counter import (
    increment_step,
    run_binary_counter,
    worked_examples,
)
from foundations_vi_lab.g03_currency.dynamic_array import (
    ArrayState,
    insert_step,
    run_dynamic_array,
    worked_resize_example,
)
from foundations_vi_lab.g03_currency.ledger import telescoping_holds


def test_binary_counter_worked_examples() -> None:
    examples = worked_examples()

    carry = examples["carry_0111_to_1000"]
    assert carry["before"] == "0111"
    assert carry["after"] == "1000"
    assert carry["actual_cost"] == 4
    assert carry["phi_before"] == 3
    assert carry["phi_after"] == 1
    assert carry["amortized_cost"] == 2

    noncarry = examples["noncarry_0100_to_0101"]
    assert noncarry["before"] == "0100"
    assert noncarry["after"] == "0101"
    assert noncarry["actual_cost"] == 1
    assert noncarry["phi_before"] == 1
    assert noncarry["phi_after"] == 2
    assert noncarry["amortized_cost"] == 2


def test_binary_counter_short_telescoping_run() -> None:
    value = 0b0110
    steps = []
    for index in range(1, 7):
        step = increment_step(value, index=index, width=4)
        steps.append(step)
        value += 1

    assert all(step.amortized_cost == 2 for step in steps)
    assert telescoping_holds(steps)


def test_dynamic_array_resize_worked_example() -> None:
    example = worked_resize_example()

    assert example["before"] == "size=4,capacity=4"
    assert example["after"] == "size=5,capacity=8"
    assert example["resized"] is True
    assert example["actual_cost"] == 5
    assert example["phi_before"] == 4
    assert example["phi_after"] == 2
    assert example["amortized_cost"] == 3
    assert example["final_size"] == 5
    assert example["final_capacity"] == 8


def test_dynamic_array_short_telescoping_run() -> None:
    state = ArrayState(size=0, capacity=1)
    steps = []
    resize_amortized = []
    for index in range(1, 12):
        state, step, resized = insert_step(state, index=index)
        steps.append(step)
        if resized:
            resize_amortized.append(step.amortized_cost)

    assert all(step.amortized_cost <= 3 for step in steps)
    assert resize_amortized
    assert all(value == 3 for value in resize_amortized)
    assert telescoping_holds(steps)


def test_seeded_g3_runs() -> None:
    binary = run_binary_counter(seed=7301, length=64)
    dynamic = run_dynamic_array(seed=7302, length=64)

    assert binary.telescoping is True
    assert binary.all_amortized_exact_two is True
    assert dynamic.telescoping is True
    assert dynamic.all_amortized_at_most_three is True
    assert dynamic.resize_steps_exact_three is True
