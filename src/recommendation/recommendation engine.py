def generate_recommendations(age, sex, weight, height, bmi, neck_circumference, alcohol_use):
    recommendations = []

    # Evaluación de IMC
    if bmi >= 25 and bmi < 30:
        recommendations.append("Se encuentra en rango de sobrepeso. Reducir el IMC mediante dieta y ejercicio puede disminuir el riesgo de apnea del sueño.")
    elif bmi >= 30:
        recommendations.append("El IMC indica obesidad, principal factor de riesgo para apnea. Se recomienda programa de pérdida de peso supervisado.")

    # Edad
    if age >= 40:
        recommendations.append("La edad incrementa el riesgo de apnea. Se sugiere una evaluación clínica periódica del sueño.")
    elif age < 30:
        recommendations.append("Aunque es joven, es importante mantener hábitos saludables para prevenir apnea temprana.")

    # Género
    if sex.lower() == "male":
        recommendations.append("El género masculino presenta mayor riesgo de apnea. Esté atento a síntomas como ronquidos fuertes o somnolencia diurna.")
    else:
        recommendations.append("El riesgo de apnea en mujeres es menor, pero puede aumentar después de la menopausia.")

    # Circunferencia del cuello
    if neck_circumference >= 40:
        recommendations.append("El perímetro cervical elevado es un indicador de riesgo. Se recomienda pérdida de grasa corporal total.")
    elif neck_circumference >= 37:
        recommendations.append("El perímetro cervical podría incrementar el riesgo de apnea. Considere control de peso y actividad física.")

    # Peso vs Altura
    ideal_weight = 22 * ((height / 100) ** 2)
    if weight > ideal_weight:
        recommendations.append("El peso está por encima del ideal. Una reducción de peso puede mejorar la calidad del sueño y disminuir la apnea.")

    if alcohol_use:
        recommendations.append("Evite consumo de alcohol antes de dormir para disminuir episodios de apnea.")

    # Recomendaciones generales aplicables a todos
    recommendations.append("Evite dormir boca arriba; dormir de lado reduce la probabilidad de obstrucción de las vías respiratorias.")
    recommendations.append("Consulte un especialista en sueño si presenta síntomas como ronquidos intensos o pausas respiratorias.")

    return recommendations

'''
# Ejemplo de uso:
if __name__ == "__main__":
    patient_data = {
        "age": 25,
        "sex": "Male",
        "weight": 80,
        "height": 172,
        "bmi": 27.04,
        "neck_circumference": 35,
        "alcohol_use":True
    }

    recs = generate_recommendations(**patient_data)
    for rec in recs:
        print(f"- {rec}")
'''