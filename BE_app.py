from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from pathlib import Path
from datetime import datetime
from PIL import Image
import traceback
import json

# Import triedy pre analýzu zo skriptu renemaPhotos.py
from renemaPhotos import RoofAnalysisServer

# Import triedy pre analýzu osvetlenia.
# Uistite sa, že súbor s touto triedou sa volá platne (napr. roof_analysis.py, nie roof-analysis.py)
from roof_analysis import PhotoAnalyzer


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

@app.route("/api/heatmap/<filename>", methods=["GET"])
def get_heatmap(filename):
    heatmaps_dir = Path(r"D:\napady\analýza strechy\analyses")
    file_path = heatmaps_dir / filename
    if not file_path.exists():
        return jsonify({"error": "Heat map file not found"}), 404

    try:
        # Predpokladáme, že súbor má príponu .npy
        if file_path.suffix.lower() != ".npy":
            return jsonify({"error": "Unsupported file type"}), 400

        # Načítame heat mapu zo súboru
        heatmap = np.load(file_path)
        # Vytvoríme obrázok z heat mapy pomocou matplotlib
        fig, ax = plt.subplots()
        # Zobrazíme heat mapu – môžete prispôsobiť cmap a ďalšie parametre
        cax = ax.imshow(heatmap, cmap="hot")
        ax.axis('off')
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
        plt.close(fig)
        buf.seek(0)
        response = make_response(buf.getvalue())
        response.mimetype = 'image/png'
        return response
    except Exception as e:
        app.logger.error(str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

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

@app.route("/api/illumination", methods=["GET"])
def api_illumination():
    """
    REST API endpoint pre získanie analýzy osvetlenia zo súborov uložených v adresári 'analyses'.
    Predpokladá sa, že analyzované dáta sú uložené vo formáte JSON.
    """
    # Získanie cesty k adresáru s analyzami
    analyses_dir = Path("D:/napady/analýza strechy/analyses")
    if not analyses_dir.exists():
        return jsonify({"error": "Adresář s analýzami sa nenašiel"}), 404

    report = {}
    try:
        # Pre každý JSON súbor v adresári načítajte dáta
        for json_file in analyses_dir.glob("*_analysis.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                section_name = data.get("name", json_file.stem)
                # Predpokladáme, že dáta majú štruktúru s kľúčom "dates"
                report[section_name] = data["dates"]
        return jsonify(report)
    except Exception as e:
        app.logger.error(str(e))
        return jsonify({"error": str(e)}), 500

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
    
@app.route("/api/summary", methods=["GET"])
def api_summary():
    # Predpokladajme, že metóda get_analysis_summary() vracia súhrn
    try:
        from renemaPhotos import RoofAnalysisServer
        # Uveďte cestu, kde sú uložené analýzy (môže byť rovnaká ako v api/analyze)
        data_dir = "D:/napady/analýza strechy"
        server = RoofAnalysisServer(data_dir)
        summary = server.get_analysis_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/logs", methods=["GET"])
def get_logs():
    return jsonify({"logs": log_collector.get_logs()})

@app.route("/api/logs", methods=["DELETE"])
def clear_logs():
    log_collector.clear_logs()
    return jsonify({"status": "Logy boli vymazané"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)