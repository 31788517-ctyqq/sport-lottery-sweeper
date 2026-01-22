import sys
sys.path.insert(0, '.')
try:
    from backend.models.odds_companies import OddsCompany
    print('OddsCompany import successful')
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()