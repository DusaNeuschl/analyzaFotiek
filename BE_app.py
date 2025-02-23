from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from pathlib import Path
from datetime import datetime
from PIL import Image
import traceback

# Import triedy pre analýzu zo skriptu renemaPhotos.py
from renemaPhotos import RoofAnalysisServer

app = Flask(__name__)
CORS(app)  # Povolenie CORS pre všetky routy

class LogCollector:
    def __init__(self):
        self.logs = []

    def add_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"{timestamp}: {message}"
        self.logs.append(log_entry)
        print(log_entry)  # Pre debug účely vypíšeme log aj do konzoly
        
    def get_logs(self):
        return self.logs

    def clear_logs(self):
        self.logs = []

log_collector = LogCollector()

def rename_photos(directory):
    directory = Path(directory)
    renamed_count = 0
    skipped_count = 0
    error_count = 0
    
    log_collector.add_log(f"Začínam premenovanie fotografií v adresári: {directory}")
    
    for file_path in directory.glob("*.jp*g"):
        try:
            img = Image.open(file_path)
            exif_data = img._getexif()
            if exif_data:
                date_time_str = exif_data.get(306)
                if date_time_str:
                    dt = datetime.strptime(date_time_str, "%Y:%m:%d %H:%M:%S")
                    new_name = dt.strftime("%Y-%m-%d-%H-%M") + file_path.suffix.lower()
                    new_path = file_path.parent / new_name
                    
                    if new_path != file_path:
                        os.rename(file_path, new_path)
                        log_collector.add_log(f"Premenovaný súbor: {file_path.name} -> {new_name}")
                        renamed_count += 1
                    else:
                        log_collector.add_log(f"Preskočený súbor (už má správny názov): {file_path.name}")
                        skipped_count += 1
                else:
                    log_collector.add_log(f"Chýba časová pečiatka v EXIF dátach: {file_path.name}")
                    error_count += 1
            else:
                log_collector.add_log(f"Chýbajú EXIF dáta: {file_path.name}")
                error_count += 1
                
        except Exception as e:
            error_msg = f"Chyba pri spracovaní {file_path.name}: {str(e)}"
            log_collector.add_log(error_msg)
            error_count += 1

    summary = f"Dokončené premenovanie: {renamed_count} premenovaných, {skipped_count} preskočených, {error_count} chýb"
    log_collector.add_log(summary)
    return summary

@app.route("/api/rename", methods=["POST"])
def api_rename():
    data = request.get_json()
    photos_dir = data.get("photos_dir")
    
    if not photos_dir:
        return jsonify({"error": "Chýba parameter photos_dir"}), 400
    
    if not os.path.isdir(photos_dir):
        return jsonify({"error": "Adresár s fotkami sa nenašiel"}), 404

    try:
        summary = rename_photos(photos_dir)
        return jsonify({
            "status": "Fotografie boli úspešne premenované",
            "detail": summary,
            "logs": log_collector.get_logs()
        })
    except Exception as e:
        error_msg = str(e)
        log_collector.add_log(f"Kritická chyba: {error_msg}")
        return jsonify({
            "error": error_msg,
            "logs": log_collector.get_logs()
        }), 500

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json()
    photos_dir = data.get("photos_dir")
    data_dir = data.get("data_dir")
    force = data.get("force", False)

    if not photos_dir or not data_dir:
        return jsonify({"error": "Chýba parameter photos_dir alebo data_dir"}), 400
    
    if not os.path.isdir(photos_dir):
        return jsonify({"error": "Adresár s fotkami sa nenašiel"}), 404

    # Vytvorenie data_dir, ak neexistuje
    os.makedirs(data_dir, exist_ok=True)
    
    try:
        log_collector.add_log(f"Začínam analýzu fotografií...")
        log_collector.add_log(f"Zdrojový adresár: {photos_dir}")
        log_collector.add_log(f"Cieľový adresár: {data_dir}")
        if force:
            log_collector.add_log("Režim vynútenej analýzy - všetky súbory budú analyzované znova")
        
        # Inicializácia servera pre analýzu
        server = RoofAnalysisServer(data_dir)
        
        # Spustenie analýzy
        server.analyze_and_store(photos_dir, force_reanalysis=force)
        
        # Získanie sumáru
        summary = server.get_analysis_summary()
        
        # Logovanie výsledkov
        log_collector.add_log("Analýza dokončená")
        for section_name, section_data in summary.items():
            log_collector.add_log(f"Sekcia {section_name}:")
            log_collector.add_log(f"  - Analyzované dni: {', '.join(section_data['dates'])}")
            log_collector.add_log(f"  - Celkový počet meraní: {section_data['total_measurements']}")
        
        return jsonify({
            "status": "Analýza bola úspešne dokončená",
            "summary": summary,
            "logs": log_collector.get_logs()
        })
        
    except Exception as e:
        error_msg = str(e)
        log_collector.add_log(f"Kritická chyba: {error_msg}")
        log_collector.add_log(f"Stack trace: {traceback.format_exc()}")
        return jsonify({
            "error": error_msg,
            "logs": log_collector.get_logs()
        }), 500

@app.route("/api/logs", methods=["GET"])
def get_logs():
    return jsonify({"logs": log_collector.get_logs()})

@app.route("/api/logs", methods=["DELETE"])
def clear_logs():
    log_collector.clear_logs()
    return jsonify({"status": "Logy boli vymazané"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)