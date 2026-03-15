# Medi Score Calculator

# Imports
from datetime import datetime, timedelta



def validate_inputs(air_or_oxygen, consciousness, respiration_rate, spo2, temperature):
    """
    Checks the inputs are valid before calculating the score.
    Raises ValueError if any input is invalid
    """
    if air_or_oxygen not in (0, 2):
        raise ValueError("air_or_oxygen must be 0 (air) or 2 (oxygen)")

    if consciousness < 0:
        raise ValueError("consciousness value cannot be negative")

    if respiration_rate < 0:
        raise ValueError("respiration_rate cannot be negative")

    if not (0 <= spo2 <= 100):
        raise ValueError("spo2(%) must be between 0 and 100")

    if temperature < 20 or temperature > 50:
        raise ValueError("temperature value must be within realistic range")
    

def score_oxygen_use(air_or_oxygen):
    """
    Returns the score for if patient is on oxygen or air, and is raised by 2 
    if patient requires supplemental oxygen
    """
    if air_or_oxygen == 2:
        return 2
    return 0 # Patient is on air


def score_consciousness(consciousness):
    """
    Returns the score for consciousness. 0 if patient is alert/conscious, 3 if
    patient is unconscious (CVPU)
    """
    if consciousness == 0:
        return 0
    return 3 # Patient is unconscious/confused (CVPU)


def score_respiration_rate(respiration_rate):
    """
    Returns the score for respiration rate, following the ranges/thresholds
    given in the brief
    """
    if respiration_rate <= 8:
        return 3
    elif 9 <= respiration_rate <= 11:
        return 1
    elif 12 <= respiration_rate <= 20:
        return 0
    elif 21 <= respiration_rate <= 24:
        return 2
    else: # respiration_rate >= 25
        return 3
    

def score_spo2(spo2, air_or_oxygen):
    """
    Returns the score for SpO2(%), following the ranges/thresholds
    given in the brief. If SpO2 is >= 93, air_or_oxygen is needed to calculate
    final score
    """
    if spo2 <= 83:
        return 3
    elif 84 <= spo2 <= 85:
        return 2
    elif 86 <= spo2 <= 87:
        return 1
    elif 88 <= spo2 <= 92:
        return 0
    else:
        # If we get to here, SpO2 is >= 93
        # Checking whether the patient is on air or oxygen
        if air_or_oxygen == 0:
            return 0
        elif 93 <= spo2 <= 94:
            return 1
        elif 95 <= spo2 <= 96:
            return 2
        else:  # SpO2 >= 97
            return 3
        

def score_temperature(temperature):
    """
    Returns score for patient's temperature, rounded to 1 decimal place first
    """
    temperature = round(temperature, 1)

    if temperature <= 35.0:
        return 3
    elif 35.1 <= temperature <= 36.0:
        return 1
    elif 36.1 <= temperature <= 38.0:
        return 0
    elif 38.1 <= temperature <= 39.0:
        return 1
    else: # temperature >= 39.1
        return 2 
    

def calculate_medi_score(air_or_oxygen, consciousness, respiration_rate, spo2, temperature):
    """
    Calculates the total Medi score by adding all scores together (oxygen use 
    score, consciousness score, respiration rate score, SpO2 score, and
    temperature score), and returns it as an integer
    """
    validate_inputs(air_or_oxygen, consciousness, respiration_rate, spo2, temperature)

    total_score = 0 # Starting total as 0

    # Adding all scores onto total score
    total_score += score_oxygen_use(air_or_oxygen)
    total_score += score_consciousness(consciousness)
    total_score += score_respiration_rate(respiration_rate)
    total_score += score_spo2(spo2, air_or_oxygen)
    total_score += score_temperature(temperature)

    return total_score


def run_tests():
    # Examples from the brief
    assert calculate_medi_score(0, 0, 15, 95, 37.1) == 0
    assert calculate_medi_score(2, 0, 17, 95, 37.1) == 4
    assert calculate_medi_score(2, 1, 23, 88, 38.5) == 8

    # Boundary checks
    assert score_respiration_rate(8) == 3
    assert score_respiration_rate(9) == 1
    assert score_respiration_rate(11) == 1
    assert score_respiration_rate(12) == 0
    assert score_respiration_rate(20) == 0
    assert score_respiration_rate(21) == 2
    assert score_respiration_rate(24) == 2
    assert score_respiration_rate(25) == 3

    assert score_spo2(95, 0) == 0   # on air
    assert score_spo2(95, 2) == 2   # on oxygen

    # /// Bonus 2 - CBG
    assert score_cbg(3.4, True) == 3
    assert score_cbg(3.7, True) == 2
    assert score_cbg(4.5, True) == 0
    assert score_cbg(5.7, True) == 2
    assert score_cbg(6.0, True) == 3

    assert score_cbg(4.5, False) == 3
    assert score_cbg(5.0, False) == 2
    assert score_cbg(6.5, False) == 0
    assert score_cbg(8.5, False) == 2
    assert score_cbg(9.0, False) == 3

    print("All tests passed.")


# /// Bonus 1 - Alert
def calculate_medi_score_from_observation(observation):

    # Takes one observation dictionary and returns the Medi score

    return calculate_medi_score(
        observation["air_or_oxygen"],
        observation["consciousness"],
        observation["respiration_rate"],
        observation["spo2"],
        observation["temperature"]
    )


def has_score_risen_by_more_than_2_within_24_hours(observations):
    """
    Checks whether the Medi score has risen by more than 2
    within 24 hours.

    Expects a list of dictionaries with:
    - air_or_oxygen
    - consciousness
    - respiration_rate
    - spo2
    - temperature
    - recorded_at (datetime)

    Returns True if an increase of mor than 2 is found
    """
    # Sort observations by time
    observations = sorted(observations, key=lambda obs: obs["recorded_at"])

    for i in range(len(observations)):
        current_obs = observations[i]
        current_score = calculate_medi_score_from_observation(current_obs)

        for j in range(i):
            previous_obs = observations[j]
            previous_score = calculate_medi_score_from_observation(previous_obs)

            time_difference = current_obs["recorded_at"] - previous_obs["recorded_at"]

            if time_difference <= timedelta(hours=24):
                if current_score - previous_score > 2:
                    return True

    return False


# /// Bonus 2 - CBG
def score_cbg(cbg, is_fasting):
    """
    Returns the score for capillary blood glucose (CBG).
    is_fasting: True if fasting, False if 2 hours after eating
    """
    if cbg < 0:
        raise ValueError("cbg cannot be negative")

    if is_fasting:
        # Fasting ranges
        if cbg <= 3.4:
            return 3
        elif 3.5 <= cbg <= 3.9:
            return 2
        elif 4.0 <= cbg <= 5.4:
            return 0
        elif 5.5 <= cbg <= 5.9:
            return 2
        else:  # cbg >= 6.0
            return 3
    else:
        # 2 hours after eating ranges
        if cbg <= 4.5: # Adjusted from brief to avoid overlap
            return 3
        elif 4.6 <= cbg <= 5.8:
            return 2
        elif 5.9 <= cbg <= 7.8:
            return 0
        elif 7.9 <= cbg <= 8.9:
            return 2
        else:  # cbg >= 9.0
            return 3




if __name__ == "__main__":
    run_tests()

    # Patient 1
    patient_1_score = calculate_medi_score(
        air_or_oxygen=0,
        consciousness=0,
        respiration_rate=15,
        spo2=95,
        temperature=37.1
    )
    print("Patient 1 score:", patient_1_score)  # Expected: 0

    # Patient 2
    patient_2_score = calculate_medi_score(
        air_or_oxygen=2,
        consciousness=0,
        respiration_rate=17,
        spo2=95,
        temperature=37.1
    )
    print("Patient 2 score:", patient_2_score)  # Expected: 4

    # Patient 3
    patient_3_score = calculate_medi_score(
        air_or_oxygen=2,
        consciousness=1,
        respiration_rate=23,
        spo2=88,
        temperature=38.5
    )
    print("Patient 3 score:", patient_3_score)  # Expected: 8


    # /// Bonus 1 - Alert
    observation_history = [
        {
            "air_or_oxygen": 0,
            "consciousness": 0,
            "respiration_rate": 15,
            "spo2": 95,
            "temperature": 37.1,
            "recorded_at": datetime(2026, 3, 14, 10, 0)
        },
        {
            "air_or_oxygen": 2,
            "consciousness": 1,
            "respiration_rate": 23,
            "spo2": 88,
            "temperature": 38.5,
            "recorded_at": datetime(2026, 3, 15, 9, 0)
        }
    ]

    trend_alert = has_score_risen_by_more_than_2_within_24_hours(observation_history)
    print("Trend alert:", trend_alert)  # Expected: True


    # /// Bonus 2 - CBG
    fasting_cbg_score = score_cbg(3.7, True)
    print("Fasting CBG score:", fasting_cbg_score)  # Expected: 2

    post_meal_cbg_score = score_cbg(8.5, False)
    print("Post-meal CBG score:", post_meal_cbg_score)  # Expected: 2