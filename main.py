from flask import Flask, send_from_directory, request, send_file, jsonify
import os
import psycopg2

app = Flask(__name__, static_folder='static')

# 환경 변수에서 Supabase PostgreSQL 접속 정보 불러오기
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def homepage():
    return open("index.html", encoding="utf-8").read()

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

@app.route('/kakutei', methods=['POST'])
def kakutei():
    from def_kakutei import analyze_kakutei_xml
    files = request.files.getlist('files')
    xml_file_list = []
    analyze_file_list = []

    for file in files:
        filename = file.filename
        if filename.lower().endswith('.xml'):
            xml_file_list.append(filename)
            analyze_file_list.append(file)

    excel_stream = analyze_kakutei_xml(analyze_file_list)

    return send_file(
        excel_stream,
        as_attachment=True,
        download_name="analyze_data.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/run-csv-tool")
def run_csv_tool():
    return "✅ TESTを処理しました！"

@app.route("/ping")
def ping():
    return "pong", 200

# 테이블 생성 (앱 최초 실행 시 1회만 호출되도록 별도 함수 구성)
def init_db():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title TEXT NOT NULL,
                start TEXT NOT NULL
            )
        ''')
        conn.commit()

# init_db()는 별도 수동 실행 권장. Supabase는 Table Editor를 통해 생성도 가능

@app.route("/api/events", methods=["GET", "POST", "DELETE"])
def handle_events():
    if request.method == "GET":
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, title, start FROM events")
            events = [{"id": str(row[0]), "title": row[1], "start": row[2]} for row in cur.fetchall()]
        return jsonify(events)

    if request.method == "POST":
        data = request.get_json()
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO events (title, start) VALUES (%s, %s) RETURNING id",
                (data["title"], data["start"])
            )
            new_id = cur.fetchone()[0]
            conn.commit()
        return jsonify({"status": "created", "id": str(new_id)}), 201

    if request.method == "DELETE":
        data = request.get_json()
        event_id = data.get("id")
        if not event_id:
            return jsonify({"error": "Missing event ID"}), 400
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM events WHERE id = %s", (event_id,))
            conn.commit()
        return jsonify({"status": "deleted"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
