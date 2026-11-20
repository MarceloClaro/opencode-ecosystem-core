"""Cálculos quantitativos com convenções explícitas — SPEC-935-R1256.

Funções puras: não coletam dados nem inferem desenho, unidades ou moeda. Valores
de taxa são frações (0.08 = 8%); quantidades monetárias permanecem na unidade
informada pelo chamador.
"""
from __future__ import annotations

import math
from statistics import NormalDist
from typing import Sequence


def _finite_real(value, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} deve ser numérico real finito.")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field} deve ser numérico real finito.")
    return result


def _positive_int(value, field: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{field} deve ser inteiro positivo.")
    return value


def _population_size(value) -> int | None:
    return None if value is None else _positive_int(value, "population_size")


def _confidence_z(confidence_level) -> tuple[float, float]:
    level = _finite_real(confidence_level, "confidence_level")
    if not 0 < level < 1:
        raise ValueError("confidence_level deve estar estritamente entre 0 e 1.")
    return level, NormalDist().inv_cdf((1.0 + level) / 2.0)


def _sample_size_result(*, n0: float, population_size: int | None, design_effect: float,
                        nonresponse_rate: float, z_score: float, confidence_level: float,
                        formula: str, outcome_model: str, assumptions: dict,
                        limitations: list[str]) -> dict:
    adjusted_infinite_n = n0 * design_effect
    if population_size is None:
        adjusted_n = adjusted_infinite_n
    else:
        adjusted_n = (
            population_size * adjusted_infinite_n
            / (population_size - 1 + adjusted_infinite_n)
            if adjusted_infinite_n > 0 else 0.0
        )
    # A população finita pode ser censitária; a função retorna um mínimo inteiro
    # de pelo menos uma unidade quando o modelo de variância degenerou em zero.
    required = max(1, math.ceil(adjusted_n - 1e-12))
    if population_size is not None:
        required = min(required, population_size)
    raw_recruitment = math.ceil(required / (1.0 - nonresponse_rate) - 1e-12)
    feasible = population_size is None or raw_recruitment <= population_size
    recruitment_target = min(raw_recruitment, population_size) if population_size is not None else raw_recruitment
    if not feasible:
        limitations.append(
            "A população disponível não comporta o alvo de recrutamento ajustado à não resposta; "
            "mesmo um censo pode não produzir os completados necessários."
        )
    return {
        "outcome_type": outcome_model,
        "population_size": population_size,
        "confidence_level": confidence_level,
        "z_score": z_score,
        "unrounded_base_n": n0,
        "unrounded_adjusted_n": adjusted_n,
        "infinite_population_n": n0,
        "required_completes": required,
        "recruitment_target_unbounded": raw_recruitment,
        "recruitment_target": recruitment_target,
        "recruitment_target_feasible": feasible,
        "design_effect": design_effect,
        "nonresponse_rate": nonresponse_rate,
        "formula": formula,
        "rounding": "ceil; at least one unit; finite result capped at population size",
        "assumptions": assumptions,
        "limitations": limitations,
        "calculation_kind": "precision-based sample-size calculation; not power analysis",
    }


def _sample_size_adjustments(design_effect, nonresponse_rate) -> tuple[float, float]:
    deff = _finite_real(design_effect, "design_effect")
    response_loss = _finite_real(nonresponse_rate, "nonresponse_rate")
    if deff <= 0:
        raise ValueError("design_effect deve ser maior que zero.")
    if not 0 <= response_loss < 1:
        raise ValueError("nonresponse_rate deve estar entre 0 (inclusive) e 1 (exclusive).")
    return deff, response_loss


def calculate_sample_size_proportion(
    population_size: int | None = None,
    margin_error: float = 0.05,
    confidence_level: float = 0.95,
    expected_proportion: float = 0.5,
    design_effect: float = 1.0,
    nonresponse_rate: float = 0.0,
) -> dict:
    """Tamanho amostral para uma proporção sob amostragem aleatória simples.

    ``expected_proportion=0.5`` é default conservador de máxima variância
    Bernoulli, não uma estimativa de heterogeneidade geográfica. `population_size`
    pode ser None para população tratada como não limitada.
    """
    population = _population_size(population_size)
    error = _finite_real(margin_error, "margin_error")
    proportion = _finite_real(expected_proportion, "expected_proportion")
    level, z = _confidence_z(confidence_level)
    deff, response_loss = _sample_size_adjustments(design_effect, nonresponse_rate)
    if not 0 < error < 1:
        raise ValueError("margin_error deve ser uma proporção entre 0 e 1.")
    if not 0 <= proportion <= 1:
        raise ValueError("expected_proportion deve estar entre 0 e 1.")
    n0 = z * z * proportion * (1.0 - proportion) / (error * error)
    proportion_choice = (
        "0.5 default de máxima variância para uma resposta Bernoulli"
        if proportion == 0.5 else "proporção esperada fornecida pelo usuário"
    )
    return _sample_size_result(
        n0=n0,
        population_size=population,
        design_effect=deff,
        nonresponse_rate=response_loss,
        z_score=z,
        confidence_level=level,
        formula="n0=Z^2*p*(1-p)/e^2; n_fpc=N*(n0*deff)/(N-1+n0*deff)",
        outcome_model="proportion",
        assumptions={
            "population_model": "Bernoulli proportion",
            "proportion_choice": proportion_choice,
            "sampling_design": "simple random sampling unless a user-supplied design_effect adjusts variance",
            "finite_population_correction": "applied when population_size is finite",
            "confidence_interpretation": "frequentist coverage under the stated sampling model; not calibration",
        },
        limitations=[
            "p representa variabilidade Bernoulli da resposta, não heterogeneidade geográfica.",
            "Representatividade, vieses, estratos/conglomerados e pesos não são inferidos pelo cálculo.",
            "design_effect e não resposta são parâmetros externos; não são estimados automaticamente.",
        ],
    )


def calculate_sample_size_mean(
    population_size: int | None,
    standard_deviation: float,
    margin_error: float,
    confidence_level: float = 0.95,
    design_effect: float = 1.0,
    nonresponse_rate: float = 0.0,
) -> dict:
    """Tamanho amostral para média, dado desvio-padrão e erro absoluto máximo."""
    population = _population_size(population_size)
    sd = _finite_real(standard_deviation, "standard_deviation")
    error = _finite_real(margin_error, "margin_error")
    level, z = _confidence_z(confidence_level)
    deff, response_loss = _sample_size_adjustments(design_effect, nonresponse_rate)
    if sd <= 0 or error <= 0:
        raise ValueError("standard_deviation e margin_error devem ser maiores que zero.")
    n0 = (z * sd / error) ** 2
    return _sample_size_result(
        n0=n0,
        population_size=population,
        design_effect=deff,
        nonresponse_rate=response_loss,
        z_score=z,
        confidence_level=level,
        formula="n0=(Z*sigma/e)^2; n_fpc=N*(n0*deff)/(N-1+n0*deff)",
        outcome_model="mean with population standard deviation",
        assumptions={
            "dispersion": "population standard deviation supplied by the user",
            "sampling_design": "simple random sampling unless a user-supplied design_effect adjusts variance",
            "finite_population_correction": "applied when population_size is finite",
            "confidence_interpretation": "frequentist coverage under the stated sampling model; not calibration",
        },
        limitations=[
            "A variabilidade populacional precisa ser estimada ou conhecida externamente.",
            "Representatividade, vieses, estratos/conglomerados e pesos não são inferidos pelo cálculo.",
            "design_effect e não resposta são parâmetros externos; não são estimados automaticamente.",
        ],
    )


def wilson_interval(successes: int, sample_size: int, confidence_level: float = 0.95) -> dict:
    """Intervalo de escore de Wilson para uma proporção binomial."""
    n = _positive_int(sample_size, "sample_size")
    if type(successes) is not int or not 0 <= successes <= n:
        raise ValueError("successes deve ser inteiro entre zero e sample_size.")
    level, z = _confidence_z(confidence_level)
    phat = successes / n
    z2 = z * z
    denominator = 1.0 + z2 / n
    center = (phat + z2 / (2.0 * n)) / denominator
    half_width = z * math.sqrt(phat * (1.0 - phat) / n + z2 / (4.0 * n * n)) / denominator
    return {
        "estimate": phat,
        "lower": max(0.0, center - half_width),
        "upper": min(1.0, center + half_width),
        "confidence_level": level,
        "method": "Wilson score interval",
        "assumptions": ["Binomial observations; independence and sampling design are not verified."],
    }


def q_exponential(x: float, q: float) -> float:
    """Exponencial de Tsallis real, com limite contínuo em q=1."""
    value = _finite_real(x, "x")
    entropic_index = _finite_real(q, "q")
    if math.isclose(entropic_index, 1.0, rel_tol=0.0, abs_tol=1e-12):
        try:
            return math.exp(value)
        except OverflowError as exc:
            raise ValueError("q-exponencial excede o domínio finito representável.") from exc
    base = 1.0 + (1.0 - entropic_index) * value
    if base <= 0:
        if entropic_index < 1.0:
            return 0.0
        raise ValueError("q-exponencial fora do domínio real para q>1 e base não positiva.")
    exponent = 1.0 / (1.0 - entropic_index)
    try:
        result = base ** exponent
    except (OverflowError, ZeroDivisionError) as exc:
        raise ValueError("q-exponencial excede o domínio finito representável.") from exc
    if not math.isfinite(result):
        raise ValueError("q-exponencial excede o domínio finito representável.")
    return result


def break_even(fixed_cost: float, unit_price: float, unit_variable_cost: float) -> dict:
    """Ponto de equilíbrio operacional em unidades vendidas."""
    fixed = _finite_real(fixed_cost, "fixed_cost")
    price = _finite_real(unit_price, "unit_price")
    variable = _finite_real(unit_variable_cost, "unit_variable_cost")
    if fixed < 0 or price <= 0 or variable < 0:
        raise ValueError("custos devem ser não negativos e preço unitário positivo.")
    contribution = price - variable
    if contribution <= 0:
        raise ValueError("preço unitário deve exceder o custo variável unitário.")
    exact = fixed / contribution
    return {"units_exact": exact, "units_to_break_even": math.ceil(exact),
            "unit_contribution": contribution,
            "formula": "fixed_cost/(unit_price-unit_variable_cost)", "currency_unit": "caller-supplied"}


def contribution_margin(unit_price: float, unit_variable_cost: float) -> dict:
    price = _finite_real(unit_price, "unit_price")
    variable = _finite_real(unit_variable_cost, "unit_variable_cost")
    if price <= 0 or variable < 0:
        raise ValueError("unit_price deve ser positivo e unit_variable_cost não negativo.")
    contribution = price - variable
    return {"unit_contribution": contribution, "margin_ratio": contribution / price,
            "formula": "(unit_price-unit_variable_cost)/unit_price", "currency_unit": "caller-supplied"}


def markup_price(cost: float, markup_rate: float) -> dict:
    base_cost = _finite_real(cost, "cost")
    rate = _finite_real(markup_rate, "markup_rate")
    if base_cost < 0 or rate < 0:
        raise ValueError("cost e markup_rate devem ser não negativos.")
    return {"selling_price": base_cost * (1.0 + rate), "markup_rate": rate,
            "formula": "cost*(1+markup_rate)", "markup_basis": "cost"}


def net_present_value(discount_rate: float, cash_flows: Sequence[float]) -> dict:
    rate = _finite_real(discount_rate, "discount_rate")
    if rate <= -1:
        raise ValueError("discount_rate deve ser maior que -1.")
    if isinstance(cash_flows, (str, bytes)) or not isinstance(cash_flows, (list, tuple)) or not cash_flows:
        raise ValueError("cash_flows deve ser uma sequência não vazia iniciando em t=0.")
    flows = [_finite_real(flow, f"cash_flows[{index}]") for index, flow in enumerate(cash_flows)]
    try:
        value = math.fsum(flow / ((1.0 + rate) ** period) for period, flow in enumerate(flows))
    except OverflowError as exc:
        raise ValueError("VPL excede o domínio finito representável.") from exc
    if not math.isfinite(value):
        raise ValueError("VPL excede o domínio finito representável.")
    return {"npv": value, "discount_rate": rate, "periods": len(flows) - 1,
            "formula": "sum(CF_t/(1+r)^t), with CF_0 undiscounted", "currency_unit": "caller-supplied"}


def cost_of_goods_sold(beginning_inventory: float, purchases: float, ending_inventory: float) -> dict:
    beginning = _finite_real(beginning_inventory, "beginning_inventory")
    bought = _finite_real(purchases, "purchases")
    ending = _finite_real(ending_inventory, "ending_inventory")
    if min(beginning, bought, ending) < 0:
        raise ValueError("estoques e compras devem ser não negativos.")
    return {"cogs": beginning + bought - ending,
            "formula": "beginning_inventory+purchases-ending_inventory", "currency_unit": "caller-supplied"}


def return_on_investment(investment: float, gross_return: float) -> dict:
    invested = _finite_real(investment, "investment")
    returned = _finite_real(gross_return, "gross_return")
    if invested <= 0:
        raise ValueError("investment deve ser maior que zero.")
    return {"roi": (returned - invested) / invested,
            "roi_percent": 100.0 * (returned - invested) / invested,
            "formula": "(gross_return-investment)/investment",
            "return_convention": "gross_return is total value returned, not incremental profit"}


def weighted_average_cost(costs: Sequence[float], quantities: Sequence[float]) -> dict:
    if (isinstance(costs, (str, bytes)) or isinstance(quantities, (str, bytes))
            or not isinstance(costs, (list, tuple)) or not isinstance(quantities, (list, tuple))
            or not costs or len(costs) != len(quantities)):
        raise ValueError("costs e quantities devem ser sequências numéricas não vazias de mesmo tamanho.")
    cost_values = [_finite_real(cost, f"costs[{i}]") for i, cost in enumerate(costs)]
    quantity_values = [_finite_real(quantity, f"quantities[{i}]") for i, quantity in enumerate(quantities)]
    if any(cost < 0 for cost in cost_values) or any(quantity < 0 for quantity in quantity_values):
        raise ValueError("custos e quantidades devem ser não negativos.")
    total_quantity = math.fsum(quantity_values)
    if total_quantity <= 0:
        raise ValueError("a soma das quantidades deve ser positiva.")
    average = math.fsum(cost * quantity for cost, quantity in zip(cost_values, quantity_values)) / total_quantity
    return {"weighted_average_cost": average, "total_quantity": total_quantity,
            "formula": "sum(unit_cost_i*quantity_i)/sum(quantity_i)", "currency_unit": "caller-supplied"}


def weighted_average_cost_of_capital(
    debt: float, equity: float, cost_of_debt: float, cost_of_equity: float, tax_rate: float
) -> dict:
    debt_value = _finite_real(debt, "debt")
    equity_value = _finite_real(equity, "equity")
    debt_rate = _finite_real(cost_of_debt, "cost_of_debt")
    equity_rate = _finite_real(cost_of_equity, "cost_of_equity")
    tax = _finite_real(tax_rate, "tax_rate")
    if debt_value < 0 or equity_value < 0 or debt_value + equity_value <= 0:
        raise ValueError("debt/equity devem ser não negativos e somar valor positivo.")
    if debt_rate < 0 or equity_rate < 0 or not 0 <= tax <= 1:
        raise ValueError("taxas de custo devem ser não negativas e tax_rate estar entre 0 e 1.")
    total = debt_value + equity_value
    value = equity_value / total * equity_rate + debt_value / total * debt_rate * (1.0 - tax)
    return {"wacc": value, "debt_weight": debt_value / total, "equity_weight": equity_value / total,
            "formula": "E/(D+E)*Re + D/(D+E)*Rd*(1-tax_rate)",
            "assumptions": ["Sem ações preferenciais; ponderações a valor de mercado devem ser fornecidas pelo usuário."]}


def internal_rate_of_return(cash_flows: Sequence[float], tolerance: float = 1e-8) -> dict:
    """Raízes reais de VPL em r>-1; não escolhe entre TIRs múltiplas.

    Usa raízes do polinômio em x=1/(1+r). Coeficientes são analisados sem
    intervalos de busca arbitrários; raízes numéricas quase reais são filtradas
    por tolerância e verificadas no polinômio original.
    """
    if isinstance(cash_flows, (str, bytes)) or not isinstance(cash_flows, (list, tuple)) or len(cash_flows) < 2:
        raise ValueError("cash_flows deve ter ao menos dois períodos.")
    flows = [_finite_real(flow, f"cash_flows[{index}]") for index, flow in enumerate(cash_flows)]
    tol = _finite_real(tolerance, "tolerance")
    if tol <= 0 or tol >= 0.01:
        raise ValueError("tolerance deve estar entre 0 e 0.01.")
    if not any(flow < 0 for flow in flows) or not any(flow > 0 for flow in flows):
        raise ValueError("TIR exige fluxos positivos e negativos.")
    coefficients = flows[:]
    while len(coefficients) > 1 and coefficients[-1] == 0:
        coefficients.pop()
    if len(coefficients) <= 1:
        roots: list[float] = []
    else:
        # NumPy já é dependência do SciPy utilizado pelo pipeline estatístico.
        import numpy as np

        polynomial_roots = np.roots(list(reversed(coefficients)))
        candidates = []
        scale = max(1.0, max(abs(value) for value in coefficients))
        for root in polynomial_roots:
            real = float(root.real)
            imaginary = float(root.imag)
            if real <= 0 or abs(imaginary) > tol * max(1.0, abs(real)):
                continue
            residual = abs(math.fsum(value * (real ** index) for index, value in enumerate(coefficients)))
            magnitude = math.fsum(abs(value) * (real ** index) for index, value in enumerate(coefficients))
            if residual > tol * max(scale, magnitude, 1.0):
                continue
            rate = 1.0 / real - 1.0
            if rate > -1 and math.isfinite(rate):
                candidates.append(rate)
        roots = []
        for candidate in sorted(candidates):
            if not roots or abs(candidate - roots[-1]) > tol * max(1.0, abs(candidate), abs(roots[-1])):
                roots.append(candidate)
    status = "no_real_root" if not roots else "unique_root" if len(roots) == 1 else "multiple_roots"
    return {"status": status, "irr": roots[0] if len(roots) == 1 else None,
            "roots": roots, "periods": len(flows) - 1,
            "formula": "solve sum(CF_t/(1+r)^t)=0 for real r>-1",
            "limitations": ["Raízes numéricas podem depender de condicionamento dos fluxos; examine escala e perfil do VPL."]}
