"""Debug script to test all page callbacks in isolation"""
import sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

FILTER = {'horizon': 'Tactical (1-12m)', 'region': 'Global', 'category': 'All', 'scenario': None}

def test(name, fn, *args):
    try:
        fn(*args)
        print(f'  OK: {name}')
    except Exception as e:
        print(f'  ERROR: {name}')
        traceback.print_exc()
        print()

# ── Data loader ────────────────────────────────────────────────────────────────
print('\n=== DATA LOADER ===')
try:
    from data import data_loader as dl
    test('get_executive_kpis', dl.get_executive_kpis, 'Global', 'All')
    test('get_forecast_accuracy_kpis', dl.get_forecast_accuracy_kpis, 'Global', 'All')
    test('get_inventory_geo', dl.get_inventory_geo, 'Global', 'All')
    test('get_capacity_utilization', dl.get_capacity_utilization, 'Global', 'All')
    test('get_risk_kpis', dl.get_risk_kpis, 'Global', 'All')
    test('get_sustainability_kpis', dl.get_sustainability_kpis, 'Global', 'All')
    test('get_regional_kpis', dl.get_regional_kpis, 'Global', 'All')
except Exception as e:
    print(f'  IMPORT ERROR: {e}')
    traceback.print_exc()

# ── KPI card ───────────────────────────────────────────────────────────────────
print('\n=== KPI CARD ===')
try:
    from components.kpi_card import kpi_row
    kpis = dl.get_executive_kpis('Global', 'All')
    result = kpi_row(kpis)
    print(f'  OK: kpi_row returned {type(result).__name__}')
except Exception as e:
    print(f'  ERROR: kpi_row failed: {e}')
    traceback.print_exc()

print('\n=== DONE ===')
