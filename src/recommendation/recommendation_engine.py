def generate_recommendations(age, sex, weight, height, bmi, neck_circumference, alcohol_use, apnea_history, sleep_difficulties):
    recommendations = []

    # BMI evaluation
    if float(bmi) >= 25 and float(bmi) < 30:
        recommendations.append("You are overweight. Reducing BMI through diet and exercise can lower the risk of sleep apnea.")
    elif float(bmi) >= 30:
        recommendations.append("BMI indicates obesity, a major risk factor for apnea. A supervised weight loss program is recommended.")

    # Age
    if float(age) >= 40:
        recommendations.append("Age increases the risk of apnea. Periodic clinical sleep evaluations are suggested.")
    elif float(age) < 30:
        recommendations.append("Although you are young, maintaining healthy habits is important to prevent early apnea.")

    # Gender
    if sex.lower() == "male":
        recommendations.append("Males have a higher risk of apnea. Be alert for symptoms such as loud snoring or daytime sleepiness.")
    else:
        recommendations.append("The risk of apnea is lower in females but may increase after menopause.")

    # Neck circumference
    if float(neck_circumference) >= 40:
        recommendations.append("A large neck circumference is a risk indicator. Total body fat reduction is recommended.")
    elif float(neck_circumference) >= 37:
        recommendations.append("Neck circumference may increase apnea risk. Consider weight control and physical activity.")

    # Weight vs Height
    ideal_weight = 22 * ((float(height) / 100) ** 2)
    if float(weight) > ideal_weight:
        recommendations.append("Your weight is above ideal. Weight reduction can improve sleep quality and decrease apnea.")

    if alcohol_use == "True":
        recommendations.append("Avoid alcohol consumption before bedtime to reduce apnea episodes.")

    # Apnea history
    if apnea_history == "True":
        recommendations.append("With a history of apnea, regular medical check-ups and symptom monitoring are essential.")

    # Sleep difficulties
    if sleep_difficulties == "True":
        recommendations.append("Sleep difficulties can worsen apnea. Consider sleep hygiene techniques and consulting a specialist.")

    # General recommendations
    recommendations.append("Avoid sleeping on your back; side sleeping reduces the likelihood of airway obstruction.")
    recommendations.append("Consult a sleep specialist if you experience symptoms like loud snoring or breathing pauses.")

    return recommendations
