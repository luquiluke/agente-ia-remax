"""
calculators.py — Calculadoras ReMax Argentina
──────────────────────────────────────────────
1. Comisión ReMax (tabla + co-broke)
2. Gastos de escritura CABA 2026
3. Rentabilidad inversor (bruta/neta)
4. Análisis pozo / fideicomiso al costo
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from market_data import GASTOS_ESCRITURA, REMAX_TABLAS


# ─── 1. Comisión ReMax ───────────────────────────────────────────────────────

@dataclass
class ResultadoComision:
    precio_venta_usd: float
    comision_bruta_pct: float
    comision_bruta_usd: float
    tabla_pct: float
    tabla_nombre: str
    neto_agente_usd: float
    franquicia_usd: float
    es_cobroke: bool
    parte_agente_cobroke_usd: float          # neto si hay co-broke 50/50
    comision_bruta_comprador_usd: float      # lo que paga el comprador
    comision_bruta_vendedor_usd: float       # lo que paga el vendedor (si split)

    def resumen(self) -> str:
        lines = [
            f"Precio de venta:        USD {self.precio_venta_usd:,.0f}",
            f"Comisión total ({self.comision_bruta_pct*100:.1f}%): USD {self.comision_bruta_usd:,.0f}",
            f"Tu tabla ({self.tabla_nombre}):     USD {self.neto_agente_usd:,.0f}",
            f"  → Franquicia:         USD {self.franquicia_usd:,.0f}",
        ]
        if self.es_cobroke:
            lines.append(f"  → Co-broke 50/50:    USD {self.parte_agente_cobroke_usd:,.0f} (tu parte)")
        return "\n".join(lines)


def calcular_comision(
    precio_venta_usd: float,
    comision_pct: float = 0.04,
    tabla_pct: float = 0.60,
    cobroke: bool = False,
    split_comprador_vendedor: float = 0.5,   # qué parte paga el comprador (0.5 = 50/50)
) -> ResultadoComision:
    """
    Calcula la comisión del agente ReMax.

    Args:
        precio_venta_usd: Precio de la operación en USD.
        comision_pct:     Porcentaje total de comisión (ej: 0.04 = 4%).
        tabla_pct:        Porcentaje de la tabla del agente (ej: 0.60 = tabla 60%).
        cobroke:          True si la operación involucra otro agente (co-broke 50/50).
        split_comprador_vendedor: Proporción que paga el comprador de la comisión total.
    """
    comision_bruta = round(precio_venta_usd * comision_pct, 2)

    # Neto agente antes de co-broke
    neto_agente_pre_cobroke = round(comision_bruta * tabla_pct, 2)
    franquicia = round(comision_bruta * (1 - tabla_pct), 2)

    # Si hay co-broke, la comisión bruta se parte 50/50 entre las dos inmobiliarias
    if cobroke:
        comision_para_agente = comision_bruta / 2
        neto_cobroke = round(comision_para_agente * tabla_pct, 2)
    else:
        neto_cobroke = neto_agente_pre_cobroke

    # Identificar nombre de la tabla
    tabla_nombre = "Tabla personalizada"
    for nombre, pct in REMAX_TABLAS.items():
        if abs(pct - tabla_pct) < 0.001:
            tabla_nombre = nombre
            break

    return ResultadoComision(
        precio_venta_usd=precio_venta_usd,
        comision_bruta_pct=comision_pct,
        comision_bruta_usd=comision_bruta,
        tabla_pct=tabla_pct,
        tabla_nombre=tabla_nombre,
        neto_agente_usd=neto_agente_pre_cobroke,
        franquicia_usd=franquicia,
        es_cobroke=cobroke,
        parte_agente_cobroke_usd=neto_cobroke,
        comision_bruta_comprador_usd=round(comision_bruta * split_comprador_vendedor, 2),
        comision_bruta_vendedor_usd=round(comision_bruta * (1 - split_comprador_vendedor), 2),
    )


# ─── 2. Gastos de escritura CABA 2026 ────────────────────────────────────────

@dataclass
class ResultadoEscritura:
    precio_escritura_usd: float
    # Comprador
    sello_comprador_usd: float
    escribano_comprador_usd: float
    rpi_usd: float
    estudio_juridico_usd: float
    total_comprador_usd: float
    total_comprador_pct: float
    # Vendedor
    sello_vendedor_usd: float
    iti_usd: float                  # 0 si no aplica (propiedad post-2018)
    escribano_vendedor_usd: float
    total_vendedor_usd: float
    total_vendedor_pct: float
    aplica_iti: bool
    nota_iti: str
    # Total de la operación
    total_operacion_usd: float

    def resumen(self) -> str:
        lines = [
            f"Precio de escritura: USD {self.precio_escritura_usd:,.0f}",
            "",
            "COMPRADOR:",
            f"  Sello CABA (ITE 50%):   USD {self.sello_comprador_usd:,.0f}",
            f"  Honorarios escribano:   USD {self.escribano_comprador_usd:,.0f}",
            f"  Registro (RPI):         USD {self.rpi_usd:,.0f}",
            f"  Estudio jurídico:       USD {self.estudio_juridico_usd:,.0f}",
            f"  TOTAL COMPRADOR:        USD {self.total_comprador_usd:,.0f} ({self.total_comprador_pct*100:.1f}%)",
            "",
            "VENDEDOR:",
            f"  Sello CABA (ITE 50%):   USD {self.sello_vendedor_usd:,.0f}",
        ]
        if self.aplica_iti:
            lines.append(f"  ITI AFIP (1.5%):        USD {self.iti_usd:,.0f}  ← aplica")
        else:
            lines.append(f"  ITI AFIP (1.5%):        NO aplica (post-2018 → Ganancias)")
        lines += [
            f"  Honorarios escribano:   USD {self.escribano_vendedor_usd:,.0f}",
            f"  TOTAL VENDEDOR:         USD {self.total_vendedor_usd:,.0f} ({self.total_vendedor_pct*100:.1f}%)",
            "",
            f"TOTAL GASTOS OPERACIÓN:  USD {self.total_operacion_usd:,.0f}",
        ]
        if self.aplica_iti:
            lines.append(f"\nNOTA: {self.nota_iti}")
        return "\n".join(lines)


def calcular_escritura(
    precio_escritura_usd: float,
    propiedad_pre_2018: bool = True,
) -> ResultadoEscritura:
    """
    Calcula gastos de escritura en CABA para 2026.

    Args:
        precio_escritura_usd: Precio declarado en la escritura (normalmente = precio real).
        propiedad_pre_2018:   True si la propiedad fue adquirida antes del 01/01/2018
                              (aplica ITI AFIP 1.5%). Las posteriores tributan Ganancias.
    """
    c = GASTOS_ESCRITURA["comprador"]
    v = GASTOS_ESCRITURA["vendedor"]

    sello_comprador = round(precio_escritura_usd * c["sello_caba_pct"], 2)
    escribano_comprador = round(precio_escritura_usd * c["escribano_pct"], 2)
    rpi = round(precio_escritura_usd * c["rpi_inscripcion_pct"], 2)
    estudio = round(precio_escritura_usd * c["estudio_juridico_pct"], 2)
    total_comprador = round(sello_comprador + escribano_comprador + rpi + estudio, 2)

    sello_vendedor = round(precio_escritura_usd * v["sello_caba_pct"], 2)
    iti = round(precio_escritura_usd * v["iti_afip_pct"], 2) if propiedad_pre_2018 else 0.0
    escribano_vendedor = round(precio_escritura_usd * v["escribano_pct"], 2)
    total_vendedor = round(sello_vendedor + iti + escribano_vendedor, 2)

    return ResultadoEscritura(
        precio_escritura_usd=precio_escritura_usd,
        sello_comprador_usd=sello_comprador,
        escribano_comprador_usd=escribano_comprador,
        rpi_usd=rpi,
        estudio_juridico_usd=estudio,
        total_comprador_usd=total_comprador,
        total_comprador_pct=round(total_comprador / precio_escritura_usd, 4),
        sello_vendedor_usd=sello_vendedor,
        iti_usd=iti,
        escribano_vendedor_usd=escribano_vendedor,
        total_vendedor_usd=total_vendedor,
        total_vendedor_pct=round(total_vendedor / precio_escritura_usd, 4),
        aplica_iti=propiedad_pre_2018,
        nota_iti=v.get("nota", ""),
        total_operacion_usd=round(total_comprador + total_vendedor, 2),
    )


# ─── 3. Rentabilidad inversor ─────────────────────────────────────────────────

@dataclass
class ResultadoRentabilidad:
    precio_compra_usd: float
    alquiler_mensual_usd: float
    expensas_mensuales_usd: float
    ingreso_neto_mensual_usd: float
    ingreso_neto_anual_usd: float
    rentabilidad_bruta_pct: float
    rentabilidad_neta_pct: float
    gastos_entrada_usd: float        # escritura + comisión compra
    payback_anos: float
    clasificacion: str               # "Excelente" / "Buena" / "Regular" / "Baja"

    def resumen(self) -> str:
        return "\n".join([
            f"Precio de compra:          USD {self.precio_compra_usd:,.0f}",
            f"Alquiler mensual:          USD {self.alquiler_mensual_usd:,.0f}",
            f"Expensas estimadas:        USD {self.expensas_mensuales_usd:,.0f}/mes",
            f"Ingreso neto mensual:      USD {self.ingreso_neto_mensual_usd:,.0f}",
            f"Rentabilidad bruta anual:  {self.rentabilidad_bruta_pct:.1f}%",
            f"Rentabilidad neta anual:   {self.rentabilidad_neta_pct:.1f}%",
            f"Gastos de entrada est.:    USD {self.gastos_entrada_usd:,.0f}",
            f"Payback estimado:          {self.payback_anos:.1f} años",
            f"Clasificación:             {self.clasificacion}",
        ])


def calcular_rentabilidad(
    precio_compra_usd: float,
    alquiler_mensual_usd: float,
    expensas_mensuales_ars: float = 0,
    tc_blue: int = 1_250,
    incluir_gastos_entrada: bool = True,
    comision_compra_pct: float = 0.04,
    tabla_pct: float = 0.60,
) -> ResultadoRentabilidad:
    """
    Calcula la rentabilidad de una inversión inmobiliaria.

    Args:
        precio_compra_usd:      Precio de compra en USD.
        alquiler_mensual_usd:   Alquiler esperado mensual en USD.
        expensas_mensuales_ars: Expensas mensuales en ARS (se convierten a USD).
        tc_blue:                Tipo de cambio blue ARS/USD.
        incluir_gastos_entrada: Si True, suma escritura + comisión al costo total.
        comision_compra_pct:    % de comisión pagada al comprar (ej: 0.04 = 4%).
        tabla_pct:              No afecta la rentabilidad del inversor (info referencia).
    """
    expensas_usd = round(expensas_mensuales_ars / tc_blue, 2) if tc_blue > 0 else 0
    ingreso_neto_mensual = round(alquiler_mensual_usd - expensas_usd, 2)
    ingreso_neto_anual = round(ingreso_neto_mensual * 12, 2)

    # Rentabilidad bruta (sin descontar expensas)
    rent_bruta = round((alquiler_mensual_usd * 12) / precio_compra_usd * 100, 2)

    # Rentabilidad neta (descontando expensas)
    rent_neta = round((ingreso_neto_anual / precio_compra_usd) * 100, 2)

    # Gastos de entrada: escritura comprador (~2.7%) + comisión
    gastos_escritura = round(precio_compra_usd * GASTOS_ESCRITURA["comprador"]["total_aprox_pct"], 2)
    gastos_comision = round(precio_compra_usd * comision_compra_pct, 2)
    gastos_entrada = round(gastos_escritura + gastos_comision, 2) if incluir_gastos_entrada else 0

    # Payback: años para recuperar la inversión total
    costo_total = precio_compra_usd + gastos_entrada
    payback = round(costo_total / ingreso_neto_anual, 1) if ingreso_neto_anual > 0 else 999

    # Clasificación
    if rent_neta >= 6:
        clasificacion = "Excelente (>6%)"
    elif rent_neta >= 4.5:
        clasificacion = "Buena (4.5-6%)"
    elif rent_neta >= 3:
        clasificacion = "Regular (3-4.5%)"
    else:
        clasificacion = "Baja (<3%)"

    return ResultadoRentabilidad(
        precio_compra_usd=precio_compra_usd,
        alquiler_mensual_usd=alquiler_mensual_usd,
        expensas_mensuales_usd=expensas_usd,
        ingreso_neto_mensual_usd=ingreso_neto_mensual,
        ingreso_neto_anual_usd=ingreso_neto_anual,
        rentabilidad_bruta_pct=rent_bruta,
        rentabilidad_neta_pct=rent_neta,
        gastos_entrada_usd=gastos_entrada,
        payback_anos=payback,
        clasificacion=clasificacion,
    )


# ─── 4. Análisis pozo / fideicomiso al costo ─────────────────────────────────

@dataclass
class ResultadoPozo:
    precio_pozo_usd: float
    superficie_m2: float
    precio_m2_pozo_usd: float
    precio_m2_mercado_usd: float
    plusvalia_esperada_pct: float
    valor_estimado_entrega_usd: float
    ganancia_bruta_usd: float
    gastos_escritura_usd: float
    ganancia_neta_usd: float
    roi_pct: float
    cuota_mensual_usd: float
    adelanto_pct: float
    adelanto_usd: float
    meses_hasta_entrega: int
    barrio: str
    clasificacion: str

    def resumen(self) -> str:
        return "\n".join([
            f"Precio en pozo:            USD {self.precio_pozo_usd:,.0f}",
            f"Superficie:                {self.superficie_m2:.0f} m²",
            f"Precio/m² en pozo:         USD {self.precio_m2_pozo_usd:,.0f}/m²",
            f"Precio/m² mercado ({self.barrio}):  USD {self.precio_m2_mercado_usd:,.0f}/m²",
            f"Plusvalía estimada:        {self.plusvalia_esperada_pct:.1f}%",
            f"Valor estimado al entregar: USD {self.valor_estimado_entrega_usd:,.0f}",
            f"Ganancia bruta:            USD {self.ganancia_bruta_usd:,.0f}",
            f"Gastos escritura (est.):   USD {self.gastos_escritura_usd:,.0f}",
            f"Ganancia neta estimada:    USD {self.ganancia_neta_usd:,.0f}",
            f"ROI estimado:              {self.roi_pct:.1f}%",
            f"Adelanto ({self.adelanto_pct*100:.0f}%):           USD {self.adelanto_usd:,.0f}",
            f"Cuota mensual estimada:    USD {self.cuota_mensual_usd:,.0f}",
            f"Meses hasta entrega:       {self.meses_hasta_entrega}",
            f"Clasificación:             {self.clasificacion}",
        ])


def calcular_pozo(
    precio_pozo_usd: float,
    superficie_m2: float,
    barrio: str,
    meses_hasta_entrega: int = 24,
    adelanto_pct: float = 0.30,
    plusvalia_esperada_pct: Optional[float] = None,
    precio_m2_mercado: Optional[float] = None,
) -> ResultadoPozo:
    """
    Analiza la rentabilidad de una unidad en pozo (fideicomiso al costo).

    Args:
        precio_pozo_usd:       Precio total de la unidad en pozo en USD.
        superficie_m2:         Superficie cubierta en m².
        barrio:                Barrio para buscar benchmark de mercado.
        meses_hasta_entrega:   Meses desde hoy hasta la entrega.
        adelanto_pct:          % del precio que se paga como adelanto (ej: 0.30 = 30%).
        plusvalia_esperada_pct: Si None, se calcula como (m² mercado - m² pozo) / m² pozo.
        precio_m2_mercado:     Si None, se usa el benchmark del barrio.
    """
    from market_data import get_benchmark

    precio_m2_pozo = round(precio_pozo_usd / superficie_m2, 0) if superficie_m2 > 0 else 0

    # Obtener precio de mercado del barrio
    bench = get_benchmark(barrio)
    if precio_m2_mercado is None:
        precio_m2_mercado = bench["avg"] if bench else precio_m2_pozo * 1.25

    # Plusvalía
    if plusvalia_esperada_pct is None:
        plusvalia_raw = ((precio_m2_mercado - precio_m2_pozo) / precio_m2_pozo) * 100
        # Cap conservador: no más de 35% ni menos de 0%
        plusvalia_esperada_pct = max(0, min(plusvalia_raw, 35.0))

    valor_al_entregar = round(precio_pozo_usd * (1 + plusvalia_esperada_pct / 100), 2)
    ganancia_bruta = round(valor_al_entregar - precio_pozo_usd, 2)

    # Gastos escritura al vender (vendedor)
    gastos_escritura = round(valor_al_entregar * GASTOS_ESCRITURA["vendedor"]["total_aprox_pct"], 2)
    ganancia_neta = round(ganancia_bruta - gastos_escritura, 2)

    roi = round((ganancia_neta / precio_pozo_usd) * 100, 1)

    # Plan de pagos estimado
    adelanto_usd = round(precio_pozo_usd * adelanto_pct, 2)
    saldo = precio_pozo_usd - adelanto_usd
    cuota_mensual = round(saldo / meses_hasta_entrega, 2) if meses_hasta_entrega > 0 else saldo

    # Clasificación
    if roi >= 25:
        clasificacion = "Excelente (ROI >25%)"
    elif roi >= 15:
        clasificacion = "Buena (ROI 15-25%)"
    elif roi >= 8:
        clasificacion = "Regular (ROI 8-15%)"
    else:
        clasificacion = "Baja (ROI <8%)"

    return ResultadoPozo(
        precio_pozo_usd=precio_pozo_usd,
        superficie_m2=superficie_m2,
        precio_m2_pozo_usd=precio_m2_pozo,
        precio_m2_mercado_usd=precio_m2_mercado,
        plusvalia_esperada_pct=plusvalia_esperada_pct,
        valor_estimado_entrega_usd=valor_al_entregar,
        ganancia_bruta_usd=ganancia_bruta,
        gastos_escritura_usd=gastos_escritura,
        ganancia_neta_usd=ganancia_neta,
        roi_pct=roi,
        adelanto_pct=adelanto_pct,
        adelanto_usd=adelanto_usd,
        cuota_mensual_usd=cuota_mensual,
        meses_hasta_entrega=meses_hasta_entrega,
        barrio=barrio,
        clasificacion=clasificacion,
    )
