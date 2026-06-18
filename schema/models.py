"""Pydantic models for the locked 6-table sgx_reit_* schema.

Single source of truth shared by:
  - the QC gate / any loader  (validation — `Model.model_validate(record)`)
  - Datalab structured extraction  (page_schema — `Model.model_json_schema()`)
  - the Claude-agent extraction skill  (the JSON shapes mirror these)

Field set follows schema/sgx_reit_schema.md. Descriptions matter: Datalab's
page_schema and any LLM extractor read them as field-level instructions, so they
are written for the extractor, not just for humans.

Conventions (enforced where Pydantic can; the rest live in the skill/QC gate):
  - money in ABSOLUTE units (S$'000 tables -> x1000), never $'000 / millions
  - percentages as plain numbers (33.9, not 0.339)
  - as-disclosed only; never compute/impute
  - source_page is provenance; null when the extractor can't attribute it
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

# canonical 15-value trade-sector taxonomy (Evelyn, Jun 17 2026; schema §5).
# used by sgx_reit_trade_mix.category AND sgx_reit_top_tenant.industry (one taxonomy).
# keep the verbatim disclosed label in *_raw and map to canonical via TRADE_ALIASES.
TRADE_CATEGORIES = (
    "Food & Beverages", "Financial & Professional Services", "Healthcare & Wellness",
    "Fashion & Accessories", "Hospitality & Leisure",
    "Infrastructure, Real Estate & Property Services", "IT & Telecommunications",
    "Other Office Trades", "Other Retail Trades", "Other Industrial Trades",
    "Logistics & Supply Chain Management", "Manufacturing", "Government Related",
    "Energy, Mining & Resources", "Departmental Store/Supermarket",
)

# old 19-value labels (and common synonyms) -> canonical 15. Extend as raw labels appear.
TRADE_ALIASES = {
    "Banking, Insurance & Financial Services": "Financial & Professional Services",
    "Professional Services": "Financial & Professional Services",
    "Beauty & Health": "Healthcare & Wellness",
    "Healthcare, Pharmaceuticals & Life Sciences": "Healthcare & Wellness",
    "Real Estate & Property Services": "Infrastructure, Real Estate & Property Services",
    "Construction & Engineering": "Infrastructure, Real Estate & Property Services",
    "Mining & Resources": "Energy, Mining & Resources",
    "Energy & Utilities": "Energy, Mining & Resources",
}

# canonical 6-value property asset-category taxonomy (Evelyn, Jun 17 2026; schema §2).
# bracketed raw labels reclassify into the canonical 6 via PROPERTY_CATEGORY_ALIASES.
PROPERTY_CATEGORIES = (
    "Industrial & Logistics", "Office", "Retail", "Data Centers",
    "Specialized", "Diversified (Commercial)",
)

PROPERTY_CATEGORY_ALIASES = {
    "Industrial": "Industrial & Logistics",
    "Logistics": "Industrial & Logistics",
    "Flatted Factories": "Industrial & Logistics",
    "Stack-up Buildings": "Industrial & Logistics",
    "Life Sciences": "Specialized",
    "Hi-Tech Buildings": "Specialized",
    "Business Space": "Specialized",
}

LandTenure = Literal["Freehold", "Leasehold"]
PropertyStatus = Literal["active", "divested", "held_for_sale"]
Statement = Literal["revenue", "expense", "adjustment"]


class Flag(BaseModel):
    """An extraction caveat raised when something looks off / non-standard, so a human
    can verify rather than the pipeline forcing a universal rule (meeting Jun 17 2026).
    Examples: dpu_half_year_split, same_property_diff_lease, divested_partial_data,
    full_consolidation_partial_ownership."""
    type: str = Field(description="short machine key, e.g. dpu_half_year_split")
    scope: Optional[str] = Field(None, description="field/row the flag applies to")
    note: Optional[str] = Field(None, description="human-readable explanation")


class ManagerEntity(BaseModel):
    role: Literal["reit_manager", "property_manager", "trustee", "sponsor",
                  "operator", "master_lessee"] = Field(description="the entity's role")
    company_name: str = Field(description="the company/entity name as printed")


class Profile(BaseModel):
    """sgx_reit_profile — one per trust. REIT-specific columns only."""
    symbol: str = Field(description="SGX ticker with .SI suffix, e.g. C38U.SI")
    sub_sector: Optional[str] = Field(
        None, description="REIT sub-sector: one of Retail | Office | Industrial | "
        "Hospitality | Healthcare | Data Centre | Diversified")
    management: list[ManagerEntity] = Field(
        default_factory=list,
        description="manager entities and their roles (reit_manager, trustee, "
        "property_manager, sponsor, operator, master_lessee)")
    income_model: Optional[str] = Field(
        None, description="conventional | master_lease | mcmgi | management_contract "
        "| entrusted_management | fri | mixed (working metadata; not loaded to DB)")
    source_page: Optional[int] = None


class PropertyTenant(BaseModel):
    """One tenant in a property's major/top-tenant list (Property.major_tenants).
    A property often discloses several major tenants (and sometimes a per-property top-N)."""
    name: str = Field(description="tenant name as printed")
    industry: Optional[str] = Field(
        None, description="canonical 15-value trade sector, when classifiable")
    pct: Optional[float] = Field(
        None, description="this tenant's share of the property's GRI/income, % plain number")


class Property(BaseModel):
    """sgx_reit_property — one per (symbol, property, financial_year)."""
    symbol: str = Field(description="SGX ticker with .SI suffix")
    financial_year: int = Field(description="calendar year the fiscal year ends")
    property_name: str = Field(description="property name as printed")
    country: Optional[str] = None
    category: Optional[str] = Field(
        None, description="property asset category, mapped to the canonical 6: "
        + "; ".join(PROPERTY_CATEGORIES))
    category_raw: Optional[str] = Field(
        None, description="verbatim disclosed asset type (e.g. 'Hi-Tech Buildings'); "
        "maps to category via PROPERTY_CATEGORY_ALIASES")
    address: Optional[str] = None
    ownership: Optional[float] = Field(None, description="% stake held by the trust")
    market_valuation: Optional[float] = Field(
        None, description="carrying value from the audited financial statements / "
        "portfolio statement, absolute units (NOT $'000)")
    valuation_date: Optional[str] = Field(None, description="FS valuation date YYYY-MM-DD")
    currency: Optional[str] = None
    net_property_income: Optional[float] = Field(None, description="as-disclosed only")
    gross_revenue: Optional[float] = None
    npi_pct: Optional[float] = Field(
        None, description="this property's share of portfolio net property income (NPI), % plain "
        "number — when the report discloses the contribution as a percentage (not an absolute)")
    occupancy_rate: Optional[float] = Field(None, description="percent, plain number")
    trade_mix: Optional[dict[str, float]] = Field(
        None, description="per-property trade mix {category: pct}, when disclosed")
    major_tenants: list[PropertyTenant] = Field(
        default_factory=list,
        description="major/top tenants for this property (often several); was major_tenant text")
    gla: Optional[float] = Field(
        None, description="gross lettable area — the LETTABLE area; do NOT fill from gross "
        "FLOOR area (that is gfa). Distinct from nla (net lettable).")
    nla: Optional[float] = Field(None, description="net lettable area (distinct from gla/gfa)")
    gfa: Optional[float] = Field(
        None, description="gross floor area — the built floor area (NOT lettable area); keep "
        "separate from gla/nla. Many cards disclose GFA, not GLA.")
    land_tenure: Optional[LandTenure] = Field(
        None, description="Freehold or Leasehold ONLY; verbatim wording -> tenure_raw")
    effective_date: Optional[str] = Field(None, description="land-lease start YYYY-MM-DD")
    lease_term_years: Optional[float] = Field(None, description="land-lease term, e.g. 99")
    lease_expiry_date: Optional[str] = Field(None, description="YYYY-MM-DD when disclosed")
    tenure_raw: Optional[str] = Field(None, description="verbatim tenure disclosure")
    status: PropertyStatus = "active"
    flags: list[Flag] = Field(
        default_factory=list,
        description="caveats to verify, e.g. same_property_diff_lease, divested_partial_data, "
        "full_consolidation_partial_ownership (100% financials on a <100% owned asset)")
    source_page: Optional[int] = None


class Performance(BaseModel):
    """sgx_reit_performance — one per (symbol, financial_year)."""
    symbol: str
    financial_year: int
    portfolio_value: Optional[float] = Field(
        None, description="headlined portfolio valuation incl. proportionate JV interests")
    properties_location: Optional[str] = None
    gross_revenue: Optional[float] = None
    net_property_income: Optional[float] = None
    net_distributable_income: Optional[float] = None
    dpu: Optional[float] = Field(None, description="full-year distribution per unit, cents")
    distribution_record: Optional[list[dict]] = Field(
        None, description="per-period distributions when split (e.g. H1/H2): "
        "[{period, dpu, ex_date, pay_date}] — captures the half-year DPU case")
    number_of_unitholders: Optional[int] = None
    currency: Optional[str] = None
    date: Optional[str] = Field(None, description="FY-end date YYYY-MM-DD")
    flags: list[Flag] = Field(
        default_factory=list,
        description="caveats to verify, e.g. dpu_half_year_split")
    source_page: Optional[int] = None


class TopTenant(BaseModel):
    """sgx_reit_top_tenant — one per (symbol, financial_year, rank)."""
    symbol: str
    financial_year: int
    rank: int
    client_name: Optional[str] = Field(
        None, description="tenant name; null if anonymised (was tenant_name; renamed to "
        "match sgx_manual_input.top_10_gri%_customers.client_name)")
    industry: Optional[str] = Field(
        None, description="tenant trade sector, mapped to the canonical 15-value taxonomy "
        "(was trade_sector; renamed to match prod 'industry')")
    revenue_pct: Optional[float] = Field(
        None, description="GRI/revenue percent, plain number e.g. 5.0 (was gri_percentage; "
        "prod stores it as a 0.05 fraction — convert at the manual_input transform)")
    pct_basis: Optional[str] = Field(
        None, description="denominator: gri | gri_excl_gto | gross_revenue | "
        "rental_income | nla | outlet_sales | ...")
    source_page: Optional[int] = None


class TradeMix(BaseModel):
    """sgx_reit_trade_mix — REIT-level, as disclosed (never rolled up)."""
    symbol: str
    financial_year: int
    category: str = Field(
        description="mapped to the canonical 15-value taxonomy: "
        + "; ".join(TRADE_CATEGORIES))
    category_raw: Optional[str] = Field(None, description="verbatim disclosed label")
    pct: Optional[float] = Field(None, description="percent, plain number")
    pct_basis: Optional[str] = Field(None, description="the denominator the trust used")
    source_page: Optional[int] = None


class FinancialBreakdownItem(BaseModel):
    """One categorized line in a revenue / operating-expense breakdown — mirrors
    sgx_manual_input.income_stmt_metrics.*_breakdown shape ({class, amount, category})."""
    category: str = Field(
        description="disclosed line label, e.g. 'Property rental', 'Management fees'")
    amount: Optional[float] = Field(None, description="absolute units")
    cls: Optional[str] = Field(
        None, alias="class",
        description="standardized class bucket, e.g. 'Product/Service Sales', "
        "'General & Admin', 'Salaries & Benefits', 'Other income', 'Other expenses'")
    model_config = {"populate_by_name": True}


class FinancialNoteLine(BaseModel):
    """One audited Statement-of-Total-Return note line — our granular reconciliation
    anchor, kept in FinancialStatement.line_items (finer than the standardized metrics).
    Adjustments are SIGNED so revenue - expense + Σadjustment = total return."""
    statement: Statement = Field(description="revenue | expense | adjustment")
    component: str = Field(
        description="canonical key, e.g. base_rental, property_tax, management_fee_base")
    amount: Optional[float] = Field(None, description="absolute units; adjustments SIGNED")
    label_raw: Optional[str] = Field(None, description="exact audited note line")
    source_page: Optional[int] = None


class IncomeStmtMetrics(BaseModel):
    """1:1 with prod sgx_manual_input.income_stmt_metrics (jsonb). extra='allow' keeps it
    forward-compatible with non-REIT SGX companies (banks/airlines carry different keys,
    e.g. interest_income, int_income_breakdown)."""
    model_config = {"extra": "allow", "populate_by_name": True}
    total_revenue: Optional[float] = Field(None, description="gross revenue; tie-out anchor")
    cost_of_revenue: Optional[float] = Field(
        None, description="= property opex for a REIT; POSITIVE magnitude (like prod)")
    gross_income: Optional[float] = Field(None, description="= NPI for a REIT")
    operating_income: Optional[float] = None
    operating_expense: Optional[float] = Field(
        None, description="POSITIVE magnitude (like prod)")
    ebit: Optional[float] = None
    ebitda: Optional[float] = None
    pretax_income: Optional[float] = None
    income_taxes: Optional[float] = Field(
        None, description="tax expense as a POSITIVE magnitude (like prod)")
    net_income: Optional[float] = Field(None, description="total return for the year, after tax")
    non_operating_income_or_loss: Optional[float] = Field(None, description="SIGNED")
    interest_expense_non_operating: Optional[float] = Field(
        None, description="finance costs; POSITIVE magnitude (like prod)")
    diluted_shares_outstanding: Optional[float] = None
    # REIT keys prod keeps inside this blob
    net_property_sales: Optional[float] = Field(None, description="divestment gain/loss; 0 if none")
    funds_from_operation: Optional[float] = Field(
        None, description="FFO — capture if the report discloses it; else null (many SG REITs "
        "report distributable income instead, see performance.net_distributable_income). Not "
        "equal to net_income, which includes non-cash fair-value items FFO excludes.")
    # extra='allow' also carries `_derived`: list[str] — the computed (not disclosed) fields
    # in this blob (operating_income, ebit, ebitda, non_operating_income_or_loss,
    # interest_expense_non_operating), so derived values never masquerade as disclosed.
    unitholders: Optional[float] = Field(None, description="attributable to unitholders")
    perpetual_security_holders: Optional[float] = None
    minorities: Optional[float] = Field(None, description="non-controlling interests")
    revenue_breakdown: list[FinancialBreakdownItem] = Field(default_factory=list)
    operating_expense_breakdown: list[FinancialBreakdownItem] = Field(default_factory=list)


class BalanceSheetMetrics(BaseModel):
    """1:1 with prod sgx_manual_input.balance_sheet_metrics (jsonb). extra='allow' for
    sector-specific keys (banks carry gross_loan, rwa, deposits, …)."""
    model_config = {"extra": "allow"}
    total_asset: Optional[float] = None
    total_equity: Optional[float] = None
    total_liabilities: Optional[float] = None
    working_capital: Optional[float] = None
    total_current_asset: Optional[float] = None
    total_non_current_asset: Optional[float] = None
    total_current_liabilities: Optional[float] = None
    total_non_current_liabilities: Optional[float] = None


class CashFlowMetrics(BaseModel):
    """1:1 with prod sgx_manual_input.cash_flow_metrics (jsonb)."""
    model_config = {"extra": "allow"}
    operating_cash_flow: Optional[float] = None
    investing_cash_flow: Optional[float] = None
    financing_cash_flow: Optional[float] = None
    net_cash_flow: Optional[float] = None
    free_cash_flow: Optional[float] = None
    capital_expenditure: Optional[float] = None


class EmployeeBreakdown(BaseModel):
    """1:1 with prod sgx_manual_input.employee_breakdown (jsonb). Usually null for REITs
    (externally managed → ~0 trust-level staff); capture manager headcount when disclosed.
    Prod nulls the whole blob when total_employee == 0."""
    model_config = {"extra": "allow"}
    total_employee: Optional[int] = None
    permanent_employee: Optional[int] = None
    contract_employee: Optional[int] = None
    others_employee: Optional[int] = None


class FinancialStatement(BaseModel):
    """sgx_reit_financial — one row per (symbol, financial_year).

    **The sector-agnostic financial-statement core**, 1:1 with the three financial-statement
    jsonb blobs of prod sgx_manual_input (income_stmt_metrics / balance_sheet_metrics /
    cash_flow_metrics), so Gerald's REITs-DB -> sgx_manual_input push is a blob-for-blob copy
    and the table generalises to non-REIT SGX later. NOT a REIT-only table conceptually.

    NOT here: REIT enrichment lives in the other tables — industry_breakdown is composed from
    top_tenant/trade_mix/property; NDI/dpu/distribution_record/portfolio_value/NPI(named) are
    sgx_reit_performance. sankey_component is derivable from the breakdowns. line_items is our
    own audit-trail extension (verbatim Statement-of-Total-Return lines; reconciliation anchor;
    Σrevenue − Σexpense + Σadjustment(signed) = income_stmt_metrics.net_income) — not in prod.
    """
    symbol: str = Field(description="SGX ticker with .SI suffix")
    financial_year: int
    currency: Optional[str] = None
    income_stmt_metrics: Optional[IncomeStmtMetrics] = None
    balance_sheet_metrics: Optional[BalanceSheetMetrics] = None
    cash_flow_metrics: Optional[CashFlowMetrics] = None
    employee_breakdown: Optional[EmployeeBreakdown] = Field(
        None, description="usually null for REITs; the one sgx_manual_input blob with no "
        "other home — kept here for 1:1 coverage")
    # our extension (not pushed to income_stmt_metrics)
    line_items: list[FinancialNoteLine] = Field(default_factory=list)
    source_page: Optional[int] = None


class REITExtraction(BaseModel):
    """Whole-document wrapper — feed as a single page_schema to extract everything."""
    profile: Optional[Profile] = None
    performance: Optional[Performance] = None
    properties: list[Property] = Field(default_factory=list)
    top_tenants: list[TopTenant] = Field(default_factory=list)
    trade_mix: list[TradeMix] = Field(default_factory=list)
    financial: Optional[FinancialStatement] = None


# section registry: name -> (model, is_list, agent-pilot filename under extracted/)
SECTIONS = {
    "profile":     (Profile,       False, "profile.json"),
    "performance": (Performance,   False, "performance.json"),
    "properties":  (Property,      True,  "properties.json"),
    "top_tenants": (TopTenant,     True,  "top_tenants.json"),
    "trade_mix":   (TradeMix,      True,  "trade_mix.json"),
    "financial":   (FinancialStatement, False, "financial.json"),
    "all":         (REITExtraction, False, None),
}
