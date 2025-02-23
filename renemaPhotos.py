import numpy as np
import cv2
from PIL import Image
from skimage import exposure
import os
from datetime import datetime
from pathlib import Path
import json
import shutil
from typing import Set, Dict, List
import hashlib

class RoofAnalysisServer:
    def __init__(self, data_dir: str):
        """
        Inicializácia servera pre analýzu strechy
        
        Args:
            data_dir: Cesta k adresáru pre ukladanie dát
        """
        self.data_dir = Path(data_dir)
        self.analysis_dir = self.data_dir / "analyses"
        self.heat_maps_dir = self.data_dir / "heat_maps"
        self.metadata_file = self.data_dir / "metadata.json"
        
        # Vytvorenie potrebných adresárov
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        self.heat_maps_dir.mkdir(parents=True, exist_ok=True)
        
        # Načítanie alebo vytvorenie metadát
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict:
        """Načíta metadata o analyzovaných súboroch"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'analyzed_files': {}}

    def _save_metadata(self):
        """Uloží metadata"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Vypočíta hash súboru pre detekciu zmien"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _get_file_info(self, file_path: Path) -> Dict:
        """Získa informácie o súbore"""
        return {
            'hash': self._calculate_file_hash(file_path),
            'size': file_path.stat().st_size,
            'mtime': file_path.stat().st_mtime
        }

    def _should_analyze_file(self, file_path: Path) -> bool:
        """Určí, či súbor potrebuje analýzu"""
        if str(file_path) not in self.metadata['analyzed_files']:
            return True
        
        current_info = self._get_file_info(file_path)
        stored_info = self.metadata['analyzed_files'][str(file_path)]
        
        return (current_info['hash'] != stored_info['hash'] or
                current_info['size'] != stored_info['size'] or
                current_info['mtime'] != stored_info['mtime'])

    def _parse_datetime_from_filename(self, filename: str) -> datetime:
        """Extrahuje dátum a čas z názvu súboru"""
        basename = Path(filename).stem
        try:
            return datetime.strptime(basename, '%Y-%m-%d-%H-%M')
        except ValueError:
            return None

    def _safe_read_image(self, img_path: Path):
        """Bezpečné načítanie obrázku s podporou Unicode cesty"""
        try:
            with open(img_path, 'rb') as f:
                img_array = np.frombuffer(f.read(), dtype=np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if img is not None:
                    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                else:
                    print(f"Varovanie: Nepodarilo sa dekódovať obrázok: {img_path.name}")
                    return None
        except Exception as e:
            print(f"Chyba pri načítaní obrázku {img_path.name}: {e}")
            return None

    def _analyze_single_image(self, image: np.ndarray) -> dict:
        """Analyzuje jednu fotografiu"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        avg_brightness = float(np.mean(gray))
        std_brightness = float(np.std(gray))
        
        heat_map = exposure.equalize_hist(gray)
        
        shadow_map = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        shadow_percentage = float((np.sum(shadow_map == 0) / shadow_map.size) * 100)
        
        return {
            'average_brightness': avg_brightness,
            'brightness_variation': std_brightness,
            'shadow_percentage': shadow_percentage,
            'heat_map': heat_map
        }

    def _load_section_data(self, section_name: str) -> Dict:
        """Načíta existujúce dáta sekcie alebo vytvorí novú štruktúru"""
        section_file = self.analysis_dir / f"{section_name}_analysis.json"
        if section_file.exists():
            with open(section_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'name': section_name,
            'dates': {}
        }

    def _save_section_data(self, section_name: str, data: Dict):
        """Uloží dáta sekcie"""
        section_file = self.analysis_dir / f"{section_name}_analysis.json"
        with open(section_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def analyze_and_store(self, photos_dir: str, force_reanalysis: bool = False):
        """
        Analyzuje fotografie a ukladá výsledky
        
        Args:
            photos_dir: Cesta k adresáru s fotografiami
            force_reanalysis: Vynúti opätovnú analýzu všetkých súborov
        """
        photos_path = Path(photos_dir)
        files_analyzed = 0
        files_skipped = 0
        
        # Prechádzanie všetkých sekcií strechy
        for section_dir in photos_path.iterdir():
            if not section_dir.is_dir():
                continue
                
            section_name = section_dir.name
            print(f"\nAnalyzujem sekciu: {section_name}")
            
            # Načítanie existujúcich dát sekcie
            section_data = self._load_section_data(section_name)
            
            # Prechádzanie všetkých fotografií v sekcii
            for img_path in section_dir.rglob('*.jp*g'):
                if not force_reanalysis and not self._should_analyze_file(img_path):
                    print(f"Preskakujem už analyzovaný súbor: {img_path.name}")
                    files_skipped += 1
                    continue
                
                img_datetime = self._parse_datetime_from_filename(img_path.name)
                if not img_datetime:
                    continue
                
                date_str = img_datetime.date().isoformat()
                if date_str not in section_data['dates']:
                    section_data['dates'][date_str] = []
                
                # Analýza fotografie
                img = self._safe_read_image(img_path)
                if img is None:
                    continue
                
                print(f"Analyzujem novú fotografiu: {img_path.name}")
                analysis = self._analyze_single_image(img)
                
                # Uloženie heat mapy
                heat_map_filename = f"{section_name}_{img_path.stem}_heat_map.npy"
                heat_map_path = self.heat_maps_dir / heat_map_filename
                np.save(heat_map_path, analysis['heat_map'])
                
                # Pridanie výsledkov analýzy
                analysis_result = {
                    'datetime': img_datetime.isoformat(),
                    'image_name': img_path.name,
                    'average_brightness': analysis['average_brightness'],
                    'brightness_variation': analysis['brightness_variation'],
                    'shadow_percentage': analysis['shadow_percentage'],
                    'heat_map_file': heat_map_filename
                }
                
                # Aktualizácia alebo pridanie nového záznamu
                existing_records = [i for i, r in enumerate(section_data['dates'][date_str]) 
                                 if r['image_name'] == img_path.name]
                if existing_records:
                    section_data['dates'][date_str][existing_records[0]] = analysis_result
                else:
                    section_data['dates'][date_str].append(analysis_result)
                
                # Aktualizácia metadát
                self.metadata['analyzed_files'][str(img_path)] = self._get_file_info(img_path)
                files_analyzed += 1
            
            # Zoradenie meraní podľa času
            for date_str in section_data['dates']:
                section_data['dates'][date_str].sort(key=lambda x: x['datetime'])
            
            # Uloženie výsledkov sekcie
            self._save_section_data(section_name, section_data)
        
        # Uloženie metadát
        self._save_metadata()
        
        print(f"\nAnalýza dokončená:")
        print(f"Analyzované súbory: {files_analyzed}")
        print(f"Preskočené súbory: {files_skipped}")

    def get_analysis_summary(self) -> dict:
        """Získa prehľad všetkých analýz"""
        summary = {}
        
        for analysis_file in self.analysis_dir.glob('*_analysis.json'):
            with open(analysis_file, 'r', encoding='utf-8') as f:
                section_data = json.load(f)
                section_name = section_data['name']
                
                summary[section_name] = {
                    'dates': list(section_data['dates'].keys()),
                    'total_measurements': sum(len(measurements) 
                                           for measurements in section_data['dates'].values())
                }
        
        return summary

# Príklad použitia
if __name__ == "__main__":
    # Inicializácia servera
    server = RoofAnalysisServer(r"D:\napady\fotky\AnalysisData")
    
    # Analýza fotografií s inkrementálnou aktualizáciou
    server.analyze_and_store(r"D:\napady\fotky\Photos")
    
    # Výpis prehľadu
    summary = server.get_analysis_summary()
    print("\nPrehľad analýz:")
    for section_name, data in summary.items():
        print(f"\nSekcia: {section_name}")
        print(f"Počet analyzovaných dní: {len(data['dates'])}")
        print(f"Celkový počet meraní: {data['total_measurements']}")
        print(f"Analyzované dátumy: {', '.join(sorted(data['dates']))}")