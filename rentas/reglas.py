"""Reglas de negocio para renta de herramientas y kits.

Aseguran que la decisión final (herramienta individual vs kit completo)
cumpla con normas de seguridad, escala del trabajo y duración.
"""

HERRAMIENTAS_POR_OFICIO = {
    "demolicion": {
        "individual": "Rotomartillo individual",
        "kit": "Kit Demolicion Completo",
    },
    "carpinteria": {
        "individual": "Lijadora orbital individual",
        "kit": "Kit Carpinteria Integral",
    },
    "plomeria": {
        "individual": "Bomba destapadora individual",
        "kit": "Kit Plomeria Profesional",
    },
    "electricidad": {
        "individual": "Taladro percutor individual",
        "kit": "Kit Electricidad Completo",
    },
    "jardineria": {
        "individual": "Cortasetos individual",
        "kit": "Kit Jardineria y Poda",
    },
    "pintura": {
        "individual": "Pistola de pintar individual",
        "kit": "Kit Pintura y Acabados",
    },
}

LIMITES = {
    "Rotomartillo individual": {"dias_max": 2, "admite_obra_mayor": False},
    "Lijadora orbital individual": {"dias_max": 2, "admite_obra_mayor": False},
    "Bomba destapadora individual": {"dias_max": 2, "admite_obra_mayor": False},
    "Taladro percutor individual": {"dias_max": 2, "admite_obra_mayor": False},
    "Cortasetos individual": {"dias_max": 2, "admite_obra_mayor": False},
    "Pistola de pintar individual": {"dias_max": 2, "admite_obra_mayor": False},

    "Kit Demolicion Completo": {"dias_max": 30, "admite_obra_mayor": True},
    "Kit Carpinteria Integral": {"dias_max": 30, "admite_obra_mayor": True},
    "Kit Plomeria Profesional": {"dias_max": 30, "admite_obra_mayor": True},
    "Kit Electricidad Completo": {"dias_max": 30, "admite_obra_mayor": True},
    "Kit Jardineria y Poda": {"dias_max": 30, "admite_obra_mayor": True},
    "Kit Pintura y Acabados": {"dias_max": 30, "admite_obra_mayor": True},
}


def es_posible(opcion: str, solicitud: dict) -> bool:
    """Evalua si una opcion cumple las reglas del negocio para la solicitud dada."""
    tipo_trabajo = solicitud.get("tipo_trabajo", "").lower()
    if tipo_trabajo in HERRAMIENTAS_POR_OFICIO:
        validas = HERRAMIENTAS_POR_OFICIO[tipo_trabajo].values()
        if opcion not in validas:
            return False

    if opcion not in LIMITES:
        return True

    limite = LIMITES[opcion]
    dias = float(solicitud.get("duracion_dias", 1))
    escala = solicitud.get("escala_trabajo", "reparacion_menor")

    if dias > limite["dias_max"]:
        return False

    if escala == "obra_mayor" and not limite["admite_obra_mayor"]:
        return False

    return True


def aplicar_reglas(preferido_modelo: str, solicitud: dict, confianza_original: float):
    """
    Aplica las reglas de negocio sobre la recomendacion del modelo.
    Garantiza que la sugerencia pertenezca al oficio correcto y explica el motivo.
    """
    tipo_trabajo = solicitud.get("tipo_trabajo", "demolicion").lower()
    escala = solicitud.get("escala_trabajo", "reparacion_menor")
    experiencia = solicitud.get("experiencia_usuario", "principiante")
    dias = float(solicitud.get("duracion_dias", 1))

    oficio_info = HERRAMIENTAS_POR_OFICIO.get(tipo_trabajo)
    if not oficio_info:
        return preferido_modelo, False, f"Recomendación: {preferido_modelo}", confianza_original

    individual = oficio_info["individual"]
    kit = oficio_info["kit"]
    validas_oficio = [individual, kit]

    if preferido_modelo not in validas_oficio:
        preferido_modelo = individual if (escala == "reparacion_menor" and dias <= 2) else kit

    # Maximo 30 dias de renta en la tienda
    if dias > 30:
        motivo = "El plazo máximo de renta continua es de 30 días según las políticas de la tienda."
        return kit, True, motivo, confianza_original

    # Si es principiante en demolicion le damos el kit con proteccion
    if tipo_trabajo == "demolicion" and experiencia == "principiante" and preferido_modelo != kit:
        motivo = f"Ajuste por seguridad: Por ser usuario principiante en demolición, se asigna el {kit} con equipo de protección y accesorios incluidos."
        return kit, True, motivo, confianza_original

    # Si son mas de 2 dias o es obra mayor se manda el kit
    if (dias > 2 or escala == "obra_mayor") and preferido_modelo != kit:
        motivo = f"Ajuste por escala y duración: Para proyectos de más de 2 días o de obra mayor, se asigna el {kit} con refacciones y accesorios."
        return kit, True, motivo, confianza_original

    # Si todo esta en orden dejamos lo que predijo el modelo
    es_kit = "kit" in preferido_modelo.lower()
    tipo_txt = "Kit completo" if es_kit else "Herramienta individual"
    motivo = f"Sugerencia directa del modelo: {preferido_modelo} ({tipo_txt})."
    return preferido_modelo, False, motivo, confianza_original
