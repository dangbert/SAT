from satsolver import Conjunction, Model, verify_model


def test_verify_model():
    system: Conjunction = [
        set([111, 112]),
        set([-111, 113]),
    ]
    model: Model = {111: False, 112: True}
    res, reason = verify_model(system, model)
    assert not res and reason == "var 113 not in model"

    model[113] = True
    res, reason = verify_model(system, model)
    assert res and reason == "system/model is True"

    model[112] = False
    res, reason = verify_model(system, model)
    assert not res and reason == "system/model is False"
