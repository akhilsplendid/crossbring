"""Swedish retail trading cost model (Avanza / Nordnet style)."""
from dataclasses import dataclass


@dataclass
class CostModel:
    # Courtage per side. Avanza Mini 0.25% (min 1 SEK), Small 0.15% (min 39 SEK),
    # Medium 0.069% (min 69 SEK). Default = Small, which fits ~50k-250k SEK accounts.
    courtage_pct: float = 0.0015
    # Half-spread + slippage per side. OMXS30 names are liquid; 0.05% is realistic
    # for market orders at the close, worse for small caps.
    slippage_pct: float = 0.0005
    # ISK/KF schablonskatt: a flat annual tax on capital, independent of gains.
    # 2025: ~0.888% of account value. Applied as a daily drag.
    isk_tax_pct_per_year: float = 0.00888

    @property
    def per_side(self) -> float:
        return self.courtage_pct + self.slippage_pct

    @property
    def daily_tax_drag(self) -> float:
        return self.isk_tax_pct_per_year / 252
