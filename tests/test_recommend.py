import pytest
from src.recommendation.recommendation_engine import generate_recommendations

def test_generate_recommendations_basic():
    recs = generate_recommendations(
        age=45,
        sex="male",
        weight=85,
        height=175,
        bmi=27,
        neck_circumference=41,
        alcohol_use="True",
        apnea_history="True",
        sleep_difficulties="True"
    )
    assert any("overweight" in r.lower() for r in recs)
    assert any("age increases" in r.lower() for r in recs)
    assert any("males have a higher risk" in r.lower() for r in recs)
    assert any("large neck circumference" in r.lower() for r in recs)
    assert any("weight is above ideal" in r.lower() for r in recs)
    assert any("avoid alcohol" in r.lower() for r in recs)
    assert any("history of apnea" in r.lower() for r in recs)
    assert any("sleep difficulties" in r.lower() for r in recs)
    assert any("avoid sleeping on your back" in r.lower() for r in recs)
    assert any("consult a sleep specialist" in r.lower() for r in recs)

@pytest.mark.parametrize("age,sex,expected", [
    (25, "male", "young"),
    (50, "female", "age increases"),
])
def test_age_and_gender_recommendations(age, sex, expected):
    recs = generate_recommendations(
        age=age,
        sex=sex,
        weight=70,
        height=170,
        bmi=22,
        neck_circumference=35,
        alcohol_use="False",
        apnea_history="False",
        sleep_difficulties="False"
    )
    combined = " ".join(recs).lower()
    assert expected in combined

def test_bmi_obesity_recommendations():
    recs = generate_recommendations(
        age=30,
        sex="female",
        weight=95,
        height=165,
        bmi=31,
        neck_circumference=36,
        alcohol_use="False",
        apnea_history="False",
        sleep_difficulties="False"
    )
    assert any("obesity" in r.lower() for r in recs)

def test_neck_circumference_recommendations():
    recs_high = generate_recommendations(
        age=30,
        sex="female",
        weight=60,
        height=165,
        bmi=22,
        neck_circumference=40,
        alcohol_use="False",
        apnea_history="False",
        sleep_difficulties="False"
    )
    recs_mid = generate_recommendations(
        age=30,
        sex="female",
        weight=60,
        height=165,
        bmi=22,
        neck_circumference=37,
        alcohol_use="False",
        apnea_history="False",
        sleep_difficulties="False"
    )
    assert any("large neck circumference" in r.lower() for r in recs_high)
    assert any("neck circumference may increase" in r.lower() for r in recs_mid)

def test_alcohol_apnea_sleep_diff_recommendations():
    recs = generate_recommendations(
        age=30,
        sex="male",
        weight=70,
        height=170,
        bmi=22,
        neck_circumference=35,
        alcohol_use="True",
        apnea_history="True",
        sleep_difficulties="True"
    )
    combined = " ".join(recs).lower()
    assert "avoid alcohol" in combined
    assert "history of apnea" in combined
    assert "sleep difficulties" in combined
