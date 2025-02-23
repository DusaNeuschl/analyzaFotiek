import os
from datetime import datetime
from dataclasses import dataclass
import cv2
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple

@dataclass
class PhotoMetadata:
    filename: str
    datetime: datetime
    position: str  # napr. "north", "south", "east", "west"
    
@dataclass
class RoofSection:
    name: str
    coordinates: List[Tuple[int, int]]  # polygón definujúci sekciu strechy

class PhotoAnalyzer:
    def __init__(self, photo_directory: str):
        self.photo_directory = photo_directory
        self.photos: List[PhotoMetadata] = []
        self.roof_sections: Dict[str, RoofSection] = {}
        
    def load_photos(self) -> None:
        """Načíta všetky fotografie z adresára a extrahuje ich metadata."""
        for filename in os.listdir(self.photo_directory):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                filepath = os.path.join(self.photo_directory, filename)
                metadata = self._extract_metadata(filepath)
                if metadata:
                    self.photos.append(metadata)
    
    def _extract_metadata(self, filepath: str) -> PhotoMetadata:
        """Extrahuje metadata z fotografie vrátane času vytvorenia."""
        try:
            image = Image.open(filepath)
            exif = {
                TAGS[k]: v
                for k, v in image._getexif().items()
                if k in TAGS
            }
            
            # Extrakcia času vytvorenia fotografie
            if 'DateTime' in exif:
                photo_datetime = datetime.strptime(exif['DateTime'], '%Y:%m:%d %H:%M:%S')
            else:
                # Použije čas vytvorenia súboru ak EXIF nie je dostupný
                photo_datetime = datetime.fromtimestamp(os.path.getctime(filepath))
            
            # Tu by sa mala doplniť logika na určenie pozície fotografie
            # Momentálne používame placeholder
            position = "unknown"
            
            return PhotoMetadata(
                filename=os.path.basename(filepath),
                datetime=photo_datetime,
                position=position
            )
        except Exception as e:
            print(f"Chyba pri spracovaní {filepath}: {str(e)}")
            return None

    def define_roof_section(self, name: str, coordinates: List[Tuple[int, int]]) -> None:
        """Definuje sekciu strechy pomocou polygónu."""
        self.roof_sections[name] = RoofSection(name=name, coordinates=coordinates)

    def analyze_illumination(self, photo_path: str, section_name: str) -> float:
        """Analyzuje intenzitu osvetlenia pre danú sekciu strechy."""
        if section_name not in self.roof_sections:
            raise ValueError(f"Sekcia {section_name} nie je definovaná")
            
        # Načítanie obrázka
        image = cv2.imread(photo_path)
        if image is None:
            raise ValueError(f"Nepodarilo sa načítať fotografiu: {photo_path}")
            
        # Vytvorenie masky pre sekciu strechy
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        points = np.array(self.roof_sections[section_name].coordinates, dtype=np.int32)
        cv2.fillPoly(mask, [points], 255)
        
        # Výpočet priemernej intenzity osvetlenia v sekcii
        masked_image = cv2.bitwise_and(image, image, mask=mask)
        hsv = cv2.cvtColor(masked_image, cv2.COLOR_BGR2HSV)
        average_brightness = np.mean(hsv[mask > 0][:, 2])
        
        return average_brightness

    def generate_illumination_report(self) -> Dict:
        """Generuje report o osvetlení pre všetky sekcie strechy."""
        report = {
            'sections': {},
            'timeline': {},
            'daily_patterns': {},
            'seasonal_patterns': {}
        }
        
        for section_name in self.roof_sections:
            section_data = []
            for photo in self.photos:
                photo_path = os.path.join(self.photo_directory, photo.filename)
                try:
                    illumination = self.analyze_illumination(photo_path, section_name)
                    section_data.append({
                        'datetime': photo.datetime,
                        'illumination': illumination,
                        'position': photo.position
                    })
                except Exception as e:
                    print(f"Chyba pri analýze {photo_path}: {str(e)}")
                    
            report['sections'][section_name] = section_data
            
        return report

    def visualize_results(self, report: Dict) -> None:
        """Vizualizuje výsledky analýzy."""
        plt.figure(figsize=(15, 10))
        
        for section_name, data in report['sections'].items():
            times = [d['datetime'] for d in data]
            illuminations = [d['illumination'] for d in data]
            
            plt.plot(times, illuminations, 'o-', label=section_name)
        
        plt.xlabel('Čas')
        plt.ylabel('Intenzita osvetlenia')
        plt.title('Analýza osvetlenia strechy')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

# Príklad použitia:
if __name__ == "__main__":
    # Inicializácia analyzátora
    analyzer = PhotoAnalyzer("AnalysisData/fotky")
    
    # Definícia sekcií strechy
    analyzer.define_roof_section("predna_cast", [
        (100, 100), (200, 100), (200, 200), (100, 200)
    ])
    
    # Načítanie a analýza fotografií
    analyzer.load_photos()
    
    # Generovanie reportu
    report = analyzer.generate_illumination_report()
    
    # Vizualizácia výsledkov
    analyzer.visualize_results(report)
