import sys
sys.path.insert(0, '.')
try:
    from backend.api.v1.draw_prediction import router
    print('draw_prediction import successful')
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()