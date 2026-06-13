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

# canonical 19-value trade-mix taxonomy (schema/sgx_reit_schema.md §5)
TRADE_CATEGORIES = (
    "Food & Beverages", "Banking, Insurance & Financial Services", "Beauty & Health",
    "Fashion & Accessories", "Hospitality & Leisure", "Real Estate & Property Services",
    "IT & Telecommunications", "Other Office Trades", "Other Retail Trades",
    "Logistics & Supply Chain Management", "Manufacturing", "Government Related",
    "Mining & Resources", "Departmental Store/Supermarket",
    "Healthcare, Pharmaceuticals & Life Sciences", "Professional Services",
    "Construction & Engineering", "Energy & Utilities", "Other Industrial Trades",
)

LandTenure = Literal["Freehold", "Leasehold"]
PropertyStatus = Literal["active", "divested", "held_for_sale"]
Statement = Literal["revenue", "expense", "adjustment"]


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


class Property(BaseModel):
    """sgx_reit_property — one per (symbol, property, financial_year)."""
    symbol: str = Field(description="SGX ticker with .SI suffix")
    financial_year: int = Field(description="calendar year the fiscal year ends")
    property_name: str = Field(description="property name as printed")
    country: Optional[str] = None
    category: Optional[str] = Field(None, description="asset class, e.g. Retail, Office")
    address: Optional[str] = None
    ownership: Optional[float] = Field(None, description="% stake held by the trust")
    market_valuation: Optional[float] = Field(
        None, description="carrying value from the audited financial statements / "
        "portfolio statement, absolute units (NOT $'000)")
    valuation_date: Optional[str] = Field(None, description="FS valuation date YYYY-MM-DD")
    currency: Optional[str] = None
    net_property_income: Optional[float] = Field(None, description="as-disclosed only")
    gross_revenue: Optional[float] = None
    occupancy_rate: Optional[float] = Field(None, description="percent, plain number")
    trade_mix: Optional[dict[str, float]] = Field(
        None, description="per-property trade mix {category: pct}, when disclosed")
    major_tenant: Optional[str] = None
    gla: Optional[float] = Field(None, description="gross lettable area")
    nla: Optional[float] = Field(None, description="net lettable area")
    land_tenure: Optional[LandTenure] = Field(
        None, description="Freehold or Leasehold ONLY; verbatim wording -> tenure_raw")
    effective_date: Optional[str] = Field(None, description="land-lease start YYYY-MM-DD")
    lease_term_years: Optional[float] = Field(None, description="land-lease term, e.g. 99")
    lease_expiry_date: Optional[str] = Field(None, description="YYYY-MM-DD when disclosed")
    tenure_raw: Optional[str] = Field(None, description="verbatim tenure disclosure")
    status: PropertyStatus = "active"
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
    dpu: Optional[float] = Field(None, description="distribution per unit, cents")
    number_of_unitholders: Optional[int] = None
    currency: Optional[str] = None
    date: Optional[str] = Field(None, description="FY-end date YYYY-MM-DD")
    source_page: Optional[int] = None


class TopTenant(BaseModel):
    """sgx_reit_top_tenant — one per (symbol, financial_year, rank)."""
    symbol: str
    financial_year: int
    rank: int
    tenant_name: Optional[str] = Field(None, description="null if anonymised")
    trade_sector: Optional[str] = None
    gri_percentage: Optional[float] = Field(None, description="percent, plain number")
    pct_basis: Optional[str] = Field(
        None, description="denominator: gri | gri_excl_gto | gross_revenue | "
        "rental_income | nla | outlet_sales | ...")
    source_page: Optional[int] = None


class TradeMix(BaseModel):
    """sgx_reit_trade_mix — REIT-level, as disclosed (never rolled up)."""
    symbol: str
    financial_year: int
    category: str = Field(
        description="mapped to the canonical 19-value taxonomy: "
        + "; ".join(TRADE_CATEGORIES))
    category_raw: Optional[str] = Field(None, description="verbatim disclosed label")
    pct: Optional[float] = Field(None, description="percent, plain number")
    pct_basis: Optional[str] = Field(None, description="the denominator the trust used")
    source_page: Optional[int] = None


class FinancialLine(BaseModel):
    """sgx_reit_financial — audited revenue/expense/adjustment note lines."""
    symbol: str
    financial_year: int
    statement: Statement = Field(description="revenue | expense | adjustment")
    component: str = Field(description="canonical key, e.g. base_rental, property_tax")
    amount: Optional[float] = Field(None, description="absolute units")
    currency: Optional[str] = None
    label_raw: Optional[str] = Field(None, description="exact audited note line")
    source_page: Optional[int] = None


class REITExtraction(BaseModel):
    """Whole-document wrapper — feed as a single page_schema to extract everything."""
    profile: Optional[Profile] = None
    performance: Optional[Performance] = None
    properties: list[Property] = Field(default_factory=list)
    top_tenants: list[TopTenant] = Field(default_factory=list)
    trade_mix: list[TradeMix] = Field(default_factory=list)
    financial: list[FinancialLine] = Field(default_factory=list)


# section registry: name -> (model, is_list, agent-pilot filename under extracted/)
SECTIONS = {
    "profile":     (Profile,       False, "profile.json"),
    "performance": (Performance,   False, "performance.json"),
    "properties":  (Property,      True,  "properties.json"),
    "top_tenants": (TopTenant,     True,  "top_tenants.json"),
    "trade_mix":   (TradeMix,      True,  "trade_mix.json"),
    "financial":   (FinancialLine, True,  "income_components.json"),
    "all":         (REITExtraction, False, None),
}
