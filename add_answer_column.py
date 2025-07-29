import sqlite3

conn = sqlite3.connect('instance/rd_center.db')
cur = conn.cursor()
try:
    cur.execute("ALTER TABLE communications ADD COLUMN answer TEXT;")
    print("answer 컬럼 추가 완료")
except Exception as e:
    print(f"실패: {e}")
finally:
    conn.commit()
    conn.close() 