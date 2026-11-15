import sys
sys.path.insert(0, '.')

from backend.models.schemas import TickerData
from backend.services.script_service import generate_structured_script

# Mock data
data = TickerData(
    symbol='PETR4.SA',
    name='Petrobras',
    price=25.30,
    change=0.45,
    change_percent=1.8,
    volume=1500000,
    news=[{'title':'Petrobras anuncia novo contrato'}],
    pe_ratio=12.5,
    market_cap=120e9,
    dividend_yield=0.04,
    debt_to_equity=0.6,
    fifty_two_week_high=30.0,
    fifty_two_week_low=20.0,
    revenue=50e9,
    net_income=8e9
)

script = generate_structured_script(data, topic='Renda Fixa')
print('--- SCRIPT ---')
print(script)
print('--- END ---')